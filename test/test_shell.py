import unittest

from shell import eval, handle_arg_case
from collections import deque
from io import StringIO
import sys
import os
import mock


class TestShell(unittest.TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_shell_eval_exception(self):
        os.mkdir("test_shell_fake")
        os.chdir("./test_shell_fake")
        with open("file1.txt", "w") as f1:
            f1.write("abc\nadc\nabc\ndef")
        with open("file2.txt", "w") as f2:
            f2.write("file2\ncontent")
        with self.assertRaises(Exception):
            eval("ls <file1.txt <file2.txt")
        os.rmdir("test_shell_fake")

    def test_shell_eval_unsafe_error(self):
        eval('_ls notExist')
        out = sys.stdout.getvalue()
        self.assertEqual("".join(out["stdout"]).strip(), '')
        self.assertEqual("".join(out["stderr"]).strip(), 'Ls: notExist: No such directory')
        self.assertNotEquals(out["exit_code"], 0)

    def test_shell_eval_no_error(self):
        eval('echo "hello world"')
        out = sys.stdout.getvalue()
        self.assertEqual("".join(out["stdout"]).strip(), 'hello world!')
        self.assertEqual("".join(out["stderr"]).strip(), '')
        self.assertEqual(out["exit_code"], 0)

    def test_shell_handle_no_arg(self):

        out = sys.stdout.getvalue()
        with mock.patch(['-c', 'echo "hello world"'], return_value="yes"):
            handle_arg_case(*[])
            out = sys.stdout.getvalue()
            self.assertEqual("".join(out["stdout"]).strip(), 'hello world!')
            self.assertEqual("".join(out["stderr"]).strip(), '')
            self.assertEqual(out["exit_code"], 0)

    def test_shell_handle_two_args(self):
        handle_arg_case(*['-c', 'echo "hello world"'])
        out = sys.stdout.getvalue()
        self.assertEqual("".join(out["stdout"]).strip(), 'hello world!')
        self.assertEqual("".join(out["stderr"]).strip(), '')
        self.assertEqual(out["exit_code"], 0)

    def test_shell_handle_wrong_num_arg(self):
        with self.assertRaises(ValueError):
            handle_arg_case(*['echo "hello world"'])

    def test_shell_handle_unexpected_arg(self):
        with self.assertRaises(ValueError):
            handle_arg_case(*['-d', 'echo "hello world"'])



if __name__ == "__main__":
    unittest.main()
