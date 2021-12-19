import unittest
import subprocess

from parsy import ParseError
from shell import eval, handle_arg_case
from io import StringIO
import sys


class OutputCapture(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout


class ErrorCapture(list):
    def __enter__(self):
        self._stderr = sys.stderr
        sys.stderr = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stderr = self._stderr


class TestShell(unittest.TestCase):
    @classmethod
    def eval(cls, flag, cmdline, shell="/comp0010/sh"):
        args = [
            shell,
            flag,
            cmdline,
        ]
        p = subprocess.run(args, capture_output=True)
        return (p.stdout.decode(), p.stderr.decode())

    def test_shell_eval_exception(self):
        out, err = self.eval("-c", "echo `_ls notExist`")
        assert len(err) > 0

    def test_shell_eval_unsafe_error(self):
        out, err = self.eval("-c", "_ls notExist")
        self.assertEqual(out.strip(), "Ls: notExist: No such directory")

    def test_shell_eval_no_error(self):
        out, err = self.eval("-c", 'echo "hello world"')
        self.assertEqual(out.strip(), "hello world")

    def test_shell_handle_no_arg(self):
        process = subprocess.Popen(
            ["/comp0010/sh"],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        output, error = process.communicate('echo "hello world"')
        self.assertEqual(output.strip(), "/comp0010> hello world\n/comp0010>")

    # has been covered
    def test_shell_handle_two_args(self):
        pass

    def test_shell_handle_wrong_num_arg(self):
        out, err = self.eval("-d", 'echo "hello world"')
        print(out, err)
        assert len(err) > 0

    def test_shell_handle_unexpected_arg(self):
        out, err = self.eval("-d", 'echo "hello world"')
        assert len(err) > 0

    def test_eval(self):
        with OutputCapture() as out:
            eval('echo "hello world"')
        self.assertEqual(out[0], "hello world")

    def test_handle_arg_case(self):
        with OutputCapture() as out:
            handle_arg_case(["shell.py", "-c", 'echo "hello world"'])
        self.assertEqual(out[0], "hello world")

    def test_eval_parse_error(self):
        with ErrorCapture() as err:
            eval("")
        self.assertGreater(len(err), 0)

    def test_eval_app_error(self):
        with ErrorCapture() as err:
            eval("cat -a")
        self.assertGreater(len(err), 0)

    def test_eval_terminal_error(self):
        with ErrorCapture() as err:
            eval("pwd < one < two")
        self.assertGreater(len(err), 0)

    def test_handle_arg_case_toomany(self):
        try:
            handle_arg_case(["shell.py", "-c", "-p", 'echo "hello world"'])
        except ValueError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_handle_arg_case_unrecognized(self):
        try:
            handle_arg_case(["shell.py", "-p", 'echo "hello world"'])
        except ValueError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
