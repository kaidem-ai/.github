#!/usr/bin/env python3
"""Reconcile Work membership and explicit per-repository categories."""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = 'PVT_kwDOEtmzRs4BoVIa'

def gh(*args):
    proc = subprocess.run(['gh', *args], capture_output=True, text=True)
    if proc.returncode: raise RuntimeError('GitHub API failed: '+proc.stderr.strip()[:1200])
    data = json.loads(proc.stdout)
    if isinstance(data, dict) and data.get('errors'):
        raise RuntimeError(str(data['errors']))
    return data

def gql(query, **variables):
    args = ['api', 'graphql', '-f', 'query='+query]
    for k, v in variables.items():
        if v is not None: args.extend(['-f', k+'='+v])
    return gh(*args)['data']

def all_items():
    out=[]; cursor=None
    query='''query($p:ID!,$cursor:String){node(id:$p){... on ProjectV2{items(first:100,after:$cursor,archivedStates:[ARCHIVED,NOT_ARCHIVED]){nodes{id isArchived content{__typename ... on Issue{id url repository{nameWithOwner}} ... on PullRequest{id url repository{nameWithOwner}}} fieldValueByName(name:"Category"){... on ProjectV2ItemFieldSingleSelectValue{name}}} pageInfo{hasNextPage endCursor}}}}}'''
    while True:
        page=gql(query,p=PROJECT,cursor=cursor)['node']['items']; out.extend(page['nodes'])
        if not page['pageInfo']['hasNextPage']: return out
        cursor=page['pageInfo']['endCursor']
        if not cursor: raise RuntimeError('Missing project cursor')

def search_open(config):
    pages=gh('api','--paginate','--slurp','-X','GET','orgs/'+config['org']+'/repos','-f','per_page=100','-f','type=all')
    repos=[r for page in pages for r in page]
    excluded={x.lower() for x in config['exclude']}
    issues=[]
    for repo in repos:
        name=repo['full_name']
        if repo['archived'] or name.lower() in excluded: continue
        pages=gh('api','--paginate','--slurp','-X','GET','repos/'+name+'/issues','-f','state=open','-f','per_page=100')
        issues.extend(i for page in pages for i in page if 'pull_request' not in i)
    if len({i['node_id'] for i in issues}) != len(issues): raise RuntimeError('Duplicate issue results')
    return issues

def plan(items, issues, mapping):
    present={x['content']['id'] for x in items if x.get('content') and x['content'].get('id')}
    additions=[i for i in issues if i['node_id'] not in present]
    updates=[]; unknown=set()
    for x in items:
        c=x.get('content') or {}; repo=(c.get('repository') or {}).get('nameWithOwner','').lower()
        if x['isArchived'] or not repo: continue
        desired=mapping.get(repo)
        current=(x.get('fieldValueByName') or {}).get('name')
        if not desired:
            if current not in {'Clients','Own'}: unknown.add(repo)
            continue
        if current != desired: updates.append((x['id'],desired))
    return additions,updates,unknown

def main():
    config=json.loads((ROOT/'boards.json').read_text())['kaidem-ai/6']; mapping={k.lower():v for k,v in config['categories'].items()}
    if set(mapping.values())-{'Clients','Own'}: raise RuntimeError('Invalid category mapping')
    fields=gql('query($p:ID!){node(id:$p){... on ProjectV2{fields(first:100){nodes{... on ProjectV2SingleSelectField{id name options{id name}}} pageInfo{hasNextPage}}}}}',p=PROJECT)['node']['fields']
    if fields['pageInfo']['hasNextPage']: raise RuntimeError('Too many project fields')
    matches=[f for f in fields['nodes'] if f.get('name')=='Category']
    if len(matches)!=1: raise RuntimeError('Category field missing or ambiguous')
    field=matches[0]; options={x['name']:x['id'] for x in field['options']}
    if not {'Clients','Own'} <= options.keys(): raise RuntimeError('Category options missing')
    items=all_items(); issues=search_open(config)
    additions,updates,unknown=plan(items,issues,mapping)
    for issue in additions:
        gql('mutation($p:ID!,$c:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$c}){item{id}}}',p=PROJECT,c=issue['node_id'])
    if additions: items=all_items(); _,updates,unknown=plan(items,[],mapping)
    for start in range(0,len(updates),5):
        batch=updates[start:start+5]
        operations=[]
        for n,(item,category) in enumerate(batch):
            operations.append('m%d:updateProjectV2ItemFieldValue(input:{projectId:%s,itemId:%s,fieldId:%s,value:{singleSelectOptionId:%s}}){projectV2Item{id}}' % (n,json.dumps(PROJECT),json.dumps(item),json.dumps(field['id']),json.dumps(options[category])))
        gql('mutation{'+ ' '.join(operations)+'}')
    print(json.dumps({'added':len(additions),'categorised':len(updates),'unclassified':sorted(unknown)}))

if __name__=='__main__':
    try: main()
    except Exception as e: print('Reconciliation failed:',e,file=sys.stderr); sys.exit(1)
