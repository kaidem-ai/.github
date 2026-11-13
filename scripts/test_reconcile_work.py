import importlib.util, pathlib, unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('reconcile',pathlib.Path(__file__).with_name('reconcile-work.py')); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_plan_preserves_archives_and_unknown(self):
  items=[{'id':'a','isArchived':False,'content':{'id':'1','repository':{'nameWithOwner':'kaidem-ai/a'}},'fieldValueByName':None},{'id':'b','isArchived':True,'content':{'id':'2','repository':{'nameWithOwner':'kaidem-ai/a'}},'fieldValueByName':None},{'id':'c','isArchived':False,'content':{'id':'3','repository':{'nameWithOwner':'kaidem-ai/z'}},'fieldValueByName':None}]
  add,update,unknown=m.plan(items,[{'node_id':'1'},{'node_id':'2'},{'node_id':'4'}],{'kaidem-ai/a':'Clients'})
  self.assertEqual(add,[{'node_id':'4'}]);self.assertEqual(update,[('a','Clients')]);self.assertEqual(unknown,{'kaidem-ai/z'})
 def test_repository_pagination_and_exclusions(self):
  repos=[[{'full_name':'kaidem-ai/a','archived':False},{'full_name':'kaidem-ai/z','archived':True}]]
  with patch.object(m,'gh',side_effect=[repos,[[{'node_id':'1'},{'node_id':'p','pull_request':{}}],[{'node_id':'2'}]]]):
   self.assertEqual([x['node_id'] for x in m.search_open({'org':'kaidem-ai','exclude':[]})],['1','2'])
 def test_correct_category_is_idempotent(self):
  item={'id':'x','isArchived':False,'content':{'id':'1','repository':{'nameWithOwner':'kaidem-ai/a'}},'fieldValueByName':{'name':'Own'}}
  self.assertEqual(m.plan([item],[],{'kaidem-ai/a':'Own'})[1],[])
if __name__=='__main__':unittest.main()
