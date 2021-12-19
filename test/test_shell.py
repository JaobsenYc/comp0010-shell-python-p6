import unittest
from abstract_syntax_tree import Substitution
from visitor import ASTVisitor
from shell import eval, handle_arg_case
from collections import deque
from io import StringIO
import sys
import os
import mock
import traceback


class TestShell(unittest.TestCase):

    # def test_shell_eval_exception(self):

    #     # try:
    #     #     ASTVisitor()._getArgs([[Substitution("_ls notExist")]])
    #     # except Exception as e:
    #     #     eval("echo `_ls notExist`")
    #     out = sys.stderr
    #     print(out)
    #     assert len(out) > 0
    #     # self.assertEqual(out, traceback.format_exc())

    # def test_shell_eval_unsafe_error(self):
    #     capturedOutput = StringIO
    #     sys.stderr = capturedOutput
    #     eval("_ls notExist")
    #     sys.stderr = sys.__stderr__
    #     assert len(capturedOutput.getvalue()) > 0

    # def test_shell_eval_no_error(self):
    #     capturedOutput = StringIO
    #     sys.stdout = capturedOutput
    #     eval('echo "hello world"')
    #     sys.stdout = sys.__stdout__
    #     assert capturedOutput.getvalue().strip() == "hello world"

    #         eval('echo "hello world"')
    #         out = sys.stdout.getvalue()
    #         print("---------->", out)
    #         self.assertEqual("".join(out["stdout"]).strip(), "hello world!")
    #         self.assertEqual("".join(out["stderr"]).strip(), "")
    #         self.assertEqual(out["exit_code"], 0)

    #     def test_shell_handle_no_arg(self):

    #         out = sys.stdout.getvalue()
    #         with mock.patch(['-c echo "hello world"'], return_value="yes"):
    #             handle_arg_case([])
    #             out = sys.stdout.getvalue()
    #             self.assertEqual("".join(out["stdout"]).strip(), "hello world!")
    #             self.assertEqual("".join(out["stderr"]).strip(), "")
    #             self.assertEqual(out["exit_code"], 0)

    #     # def test_shell_handle_two_args(self):
    #     #     handle_arg_case(["-c", 'echo "hello world"'])
    #     #     out = sys.stdout.getvalue()
    #     #     self.assertEqual("".join(out["stdout"]).strip(), "hello world!")
    #     #     self.assertEqual("".join(out["stderr"]).strip(), "")
    #     #     self.assertEqual(out["exit_code"], 0)

    #     def test_shell_handle_wrong_num_arg(self):
    #         with self.assertRaises(ValueError):
    #             handle_arg_case(['echo "hello world"'])

    #     def test_shell_handle_unexpected_arg(self):
    #         with self.assertRaises(ValueError):
    #             handle_arg_case(["-d", 'echo "hello world"'])


# if __name__ == "__main__":
#     unittest.main()
