import sys
import os
from copy import copy
from subprocess import Popen, PIPE
from elasticmetrics import __version__
from . import BaseTestCase, ROOT_PATH


class TestToolMain(BaseTestCase):
    def _run_python(self, args=(), stdin=None):
        """Run current Python with specified args. Returns
        the results of the call, stdout/stderr are decoded to text values.
        Returns (return code, stdout, stderr)
        """
        env = copy(os.environ)
        if 'PYTHONPATH' not in env or env['PYTHONPATH'] != ROOT_PATH:
            env['PYTHONPATH'] = ROOT_PATH
        command = [sys.executable]
        command.extend(args)
        py_proc = Popen(command, stdout=PIPE, stderr=PIPE, env=env)
        stdout, stderr = py_proc.communicate(stdin)
        return (py_proc.returncode, stdout.decode('utf-8'), stderr.decode('utf-8'))

    def _run_tool(self, args):
        """Run the elasticmetrics.tool module with specified args,
        and returns results, stdout/stderr are decoded to text values.

        Returns (return code, stdout, stderr)
        """
        python_args = ['-m', 'elasticmetrics.tool']
        python_args.extend(args)
        return self._run_python(python_args)

    def test_run_tool_to_show_help_message(self):
        returncode, stdout, stderr = self._run_tool(['--help'])
        self.assertEqual(returncode, os.EX_OK)
        self.assertIn(
            'usage: elasticmetrics.tool',
            stdout
        )
        self.assertEqual('', stderr)

    def test_run_tool_to_show_version(self):
        returncode, stdout, stderr = self._run_tool(['--version'])
        # Python 2 prints version to stderr, Python 3 to stdout
        output = stdout + stderr
        self.assertIn(__version__, output)

    def test_run_tool_with_invalid_arguments_exits_nok_prints_usage_stderr(self):
        returncode, stdout, stderr = self._run_tool(['--invalid'])
        self.assertGreater(returncode, 0)
        self.assertIn(
            'usage: elasticmetrics.tool',
            stderr
        )
