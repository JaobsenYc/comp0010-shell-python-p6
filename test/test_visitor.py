import unittest

from visitor import ASTVisitor
from collections import deque
from abstract_syntax_tree import AST, Substitution
import os


class TestASTVisitor(unittest.TestCase):
    def setUp(self) -> None:
        self.visitor = ASTVisitor()
        self.ast = AST()
        with open("file1.txt") as f1:
            f1.write("abc\nadc\nabc\ndef")
        with open("file2.txt") as f2:
            f2.write("file2\ncontent")

    # for single quote
    def test_visit_singlequote_empty(self):
        i = self.ast.SingleQuote("''")
        out = self.visitor.visitSingleQuote(i)
        self.assertEqual("".join(out["stdout"]), "")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_singlequote_space(self):
        i = self.ast.SingleQuote("'  '")
        out = self.visitor.visitSingleQuote(i)
        self.assertEqual("".join(out["stdout"]), "  ")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_singlequote_disable_doublequote(self):
        i = self.ast.SingleQuote("'\"\"'")
        out = self.visitor.visitSingleQuote(i)
        self.assertEqual("".join(out["stdout"]), '""')
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_singlequote_backquote(self):
        i = self.ast.SingleQuote("'`echo hello`'")
        out = self.visitor.visitSingleQuote(i)
        self.assertEqual("".join(out["stdout"]), "`echo hello`")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_singlequote_substitution_error(self):
        i = self.ast.SingleQuote("'`echo hello`'")
        out = self.visitor.visitSingleQuote(i)
        self.assertEqual("".join(out["stdout"]), "")
        self.assertEqual(
            "".join(out["stderr"]), "wrong number of command line arguments"
        )
        self.assertEqual("".join(out["exit_code"]), 1)

    def test_visit_doublequote_no_substitution(self):
        i = self.ast.DoubleQuote(["a", "b"])
        out = self.visitor.visitDoubleQuote(i)
        self.assertEqual("".join(out["stdout"]), "ab")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_doublequote_has_substitution(self):
        i = self.ast.DoubleQuote(["a", "b", self.ast.Substitution("echo c")])
        out = self.visitor.visitDoubleQuote(i)
        self.assertEqual("".join(out["stdout"]), "abc")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    # singlequote in doubleqoute?

    def test_visit_doublequote_error(self):
        i = self.ast.DoubleQuote(["a", self.ast.Substitution("ls a b"), "b"])
        out = self.visitor.visitDoubleQuote(i)
        self.assertEqual("".join(out["stdout"]), "")
        self.assertEqual(
            "".join(out["stderr"]), "wrong number of command line arguments"
        )
        self.assertEqual("".join(out["exit_code"]), 1)

    def test_visit_substitution(self):
        i = self.ast.Substitution("echo foo")
        out = self.visitor.visitSub(i)
        self.assertEqual("".join(out["stdout"]), "foo")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_substitution_error(self):
        i = self.ast.Substitution("ls a b")
        out = self.visitor.visitSub(i)
        self.assertEqual("".join(out["stdout"]), "")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_redirectin(self):
        i = self.ast.RedirectIn("file1.txt")
        out = self.visitor.visitRedirectIn(i)
        self.assertEqual("".join(out["stdout"]), "abc\nadc\nabc\ndef")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_redirectin_glob(self):
        i = self.ast.RedirectIn("*.txt")
        out = self.visitor.visitRedirectIn(i)
        self.assertEqual(
            "".join(out["stdout"]), ["abc\nadc\nabc\ndef", "file2\ncontent"]
        )
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_redirectin_error(self):
        self.assertRaises(
            FileNotFoundError,
            self.visitor.visitRedirectIn,
            self.ast.RedirectIn("file3.txt"),
        )

    def test_visit_redirectout(self):
        i = self.ast.RedirectOut("testRedirectout.txt", stdin="aaa\nbbb\nccc")
        self.visitor.visitRedirectOut(i)
        with open("testRedirectout.txt") as f:
            lines = f.readlines()
        self.assertEqual("".join(lines), "aaa\nbbb\nccc")

    # what's the best result?
    def test_visit_redirectout_no_stdin(self):
        i = self.ast.RedirectOut("testRedirectoutEmpty.txt")
        self.visitor.visitRedirectOut(i)
        with open("testRedirectoutEmpty.txt") as f:
            lines = f.readlines()
        self.assertEqual("".join(lines), "")

    def test_visit_redirectout_error(self):
        with self.assertRaises(Exception) as context:
            self.visitor.visitRedirectIn(self.ast.RedirectIn("*.txt"))
        self.assertTrue("invalid redirection out" in context.exception)

    def test_visit_call_appname_substitution(self):
        i = self.ast.Call(
            redirects=[],
            appName=self.ast.Substitution("echo echo"),
            args=[["hello world"]],
        )
        out = self.visitor.visitCall(i)
        self.assertEqual("".join(out["stdout"]), "hello world")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_call_appname_substitution_error(self):
        i = self.ast.Call(
            redirects=[],
            appName=self.ast.Substitution("cat notExist.txt"),
            args=[["hello world"]],
        )
        with self.assertRaises(Exception) as context:
            self.visitor.visitCall(i)
        self.assertTrue(
            "Cannot substitute cat notExist.txt as app name" in context.exception
        )

    def test_visit_call_redirectin(self):
        i = self.ast.Call(
            redirects=[self.ast.RedirectIn("file1.txt")],
            appName="echo",
            args=[],
        )
        out = self.visitor.visitCall(i)
        self.assertEqual("".join(out["stdout"]), "abc\nadc\nabc\ndef")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_call_redirectout(self):
        pass

    def test_visit_call_redirection_invalid(self):
        pass

    def test_visit_call_no_redirectin_input(self):
        pass

    def test_visit_call_redirectin_overwrite_input(self):
        pass

    def test_visit_call_args_doublequote(self):
        pass

    def test_visit_call_args_singlequote(self):
        pass

    def test_visit_call_args_substitution(self):
        pass

    def test_visit_call_args_exec_error(self):
        pass

    def test_visit_call_args_glob(self):
        pass

    def test_visit_call_args_multiple_glob(self):
        pass

    def test_visit_call_args_redirectout_return(self):
        pass

    def test_visit_seq_left_error(self):
        pass

    def test_visit_seq_right_error(self):
        pass

    def test_visit_seq_no_error(self):
        pass

    def test_visit_pipe_no_outleft(self):
        pass

    def test_visit_pipe_with_outleft(self):
        pass

    def test_visit_pipe_with_outleft(self):
        pass

    def test_visit_pipe_outright_error(self):
        pass

    def tearDown(self) -> None:
        os.remove("file1.txt")
        os.remove("file2.txt")
        os.remove("testRedirectout.txt")
        os.remove("testRedirectoutEmpty.txt")


if __name__ == "__main__":
    unittest.main()
