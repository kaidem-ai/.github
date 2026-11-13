#!/usr/bin/env python3
"""Run the same Work reconciliation locally without an extra credential."""
import base64, datetime, fcntl, json, os, pathlib, subprocess, sys, tempfile

REPO='kaidem-ai/.github'
STATE=pathlib.Path.home()/'Library/Application Support/Kaidem/work-sync'

def gh(*args):
    p=subprocess.run(['gh',*args],capture_output=True,text=True,timeout=60)
    if p.returncode: raise RuntimeError('GitHub API unavailable')
    return json.loads(p.stdout)

def payload(path,revision):
    d=gh('api',f'repos/{REPO}/contents/{path}?ref={revision}')
    if d.get('encoding')!='base64' or d.get('type')!='file': raise RuntimeError('Invalid source file')
    return base64.b64decode(d['content'],validate=False)

def save_state(value):
    target=STATE/'last-run.json'
    with tempfile.NamedTemporaryFile(mode='w',dir=STATE,delete=False) as f:
        os.chmod(f.name,0o600);json.dump(value,f);f.write('\n');tmp=f.name
    os.replace(tmp,target)

def main():
    STATE.mkdir(mode=0o700,parents=True,exist_ok=True)
    with (STATE/'runner.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: return 0
        stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            revision=gh('api',f'repos/{REPO}/commits/main')['sha']
            if len(revision)!=40 or any(c not in '0123456789abcdef' for c in revision): raise RuntimeError('Invalid revision')
            with tempfile.TemporaryDirectory(prefix='kaidem-work-sync-') as temp:
                root=pathlib.Path(temp);(root/'scripts').mkdir()
                (root/'boards.json').write_bytes(payload('boards.json',revision))
                (root/'scripts/reconcile-work.py').write_bytes(payload('scripts/reconcile-work.py',revision))
                p=subprocess.run([sys.executable,str(root/'scripts/reconcile-work.py')],capture_output=True,text=True,timeout=300)
                if p.returncode: raise RuntimeError('Reconciliation failed')
                data=json.loads(p.stdout)
                if not isinstance(data,dict) or not all(k in data for k in ('added','categorised','unclassified')): raise RuntimeError('Invalid result')
            save_state({'started_at':stamp,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'success','revision':revision,'added':data['added'],'categorised':data['categorised'],'unclassified_count':len(data['unclassified'])})
            return 0
        except (Exception, subprocess.TimeoutExpired) as e:
            save_state({'started_at':stamp,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'error','reason':str(e)[:160]})
            print('Work reconciliation failed:',str(e)[:160],file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
