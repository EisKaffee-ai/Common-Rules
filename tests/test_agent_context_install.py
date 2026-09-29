import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class AgentContextInstall(unittest.TestCase):
    def test_preserves_rules_and_installs_idempotent_host_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)
            text='# Project rules\nKeep the approved UI.\n'
            (project/'AGENTS.md').write_text(text)
            (project/'templates').mkdir()
            (project/'templates'/'workflow.md').write_text('Workflow rules')
            command=[sys.executable,str(ROOT/'bin/install-agent-context'),'--project',tmp]
            subprocess.run(command,check=True,capture_output=True)
            before={str(p):p.read_bytes() for p in project.rglob('*') if p.is_file()}
            subprocess.run(command,check=True,capture_output=True)
            after={str(p):p.read_bytes() for p in project.rglob('*') if p.is_file()}
            self.assertEqual(before,after)
            self.assertEqual(text,(project/'AGENTS.md').read_text())
            order=json.loads((project/'.common-rules.json').read_text())['read_order']
            self.assertEqual(order,['AGENTS.md','templates/workflow.md'])
            for host in ['.agents','.claude']:
                for name in ['warmup','reheat','preheat']:
                    self.assertTrue((project/host/'skills'/name/'SKILL.md').is_file())
                    self.assertIn('--state .common-rules/warmup-state.json',(project/host/'skills'/name/'SKILL.md').read_text())

    def test_refuses_unmanaged_skill_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp);(project/'AGENTS.md').write_text('Rules')
            skill=project/'.claude/skills/preheat/SKILL.md';skill.parent.mkdir(parents=True);skill.write_text('User skill')
            result=subprocess.run([sys.executable,str(ROOT/'bin/install-agent-context'),'--project',tmp],capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse((project/'.common-rules.json').exists())
            self.assertFalse((project/'.agents').exists())
            self.assertEqual(skill.read_text(),'User skill')

    def test_refuses_symlink_destinations_before_any_write(self):
        for destination in ['.agents','.claude/skills','.common-rules.json','.common-rules','.common-rules/warmup-state.json']:
            with self.subTest(destination=destination), tempfile.TemporaryDirectory() as tmp:
                base=Path(tmp);project=base/'project';project.mkdir();(project/'AGENTS.md').write_text('Rules')
                outside=base/'outside'
                if destination.endswith('.json'):outside.write_text('{}')
                else:outside.mkdir()
                target=project/destination;target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(outside)
                before={str(p):p.read_bytes() for p in base.rglob('*') if p.is_file() and not p.is_symlink()}
                result=subprocess.run([sys.executable,str(ROOT/'bin/install-agent-context'),'--project',str(project)],capture_output=True)
                self.assertNotEqual(result.returncode,0)
                self.assertIn(b'symlink',result.stderr.lower())
                after={str(p):p.read_bytes() for p in base.rglob('*') if p.is_file() and not p.is_symlink()}
                self.assertEqual(before,after)
