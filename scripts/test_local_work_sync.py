import importlib.util,json,pathlib,tempfile,types,unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('local_sync',pathlib.Path(__file__).with_name('local-work-sync.py')); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory();m.STATE=pathlib.Path(self.tmp.name)/'state'
 def tearDown(self): self.tmp.cleanup()
 def test_pins_sources_to_one_revision_and_records_success(self):
  sha='a'*40; seen=[]
  def payload(path,revision):seen.append((path,revision));return b'{}'
  result=types.SimpleNamespace(returncode=0,stdout='{"added":1,"categorised":2,"unclassified":[]}')
  with patch.object(m,'gh',return_value={'sha':sha}),patch.object(m,'payload',side_effect=payload),patch.object(m.subprocess,'run',return_value=result):self.assertEqual(m.main(),0)
  self.assertEqual(seen,[('boards.json',sha),('scripts/reconcile-work.py',sha)])
  state=json.loads((m.STATE/'last-run.json').read_text());self.assertEqual(state['status'],'success');self.assertEqual(state['added'],1)
 def test_failure_writes_failure_not_success(self):
  with patch.object(m,'gh',side_effect=RuntimeError('GitHub API unavailable')):self.assertEqual(m.main(),1)
  self.assertEqual(json.loads((m.STATE/'last-run.json').read_text())['status'],'error')
if __name__=='__main__':unittest.main()
