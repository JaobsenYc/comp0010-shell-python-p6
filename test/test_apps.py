from collections import deque
import unittest
import mock
from apps import (
    Pwd,
    Cd,
    Echo,
    Ls,
    Cat,
    Head,
    Tail,
    Grep,
    Cut,
    Find,
    Sort,
    Uniq,
    LocalApp,
)
import os
from hypothesis import given
from hypothesis import strategies as st


class TestApps(unittest.TestCase):
    def setUp(self) -> None:
        os.mkdir("apps")
        os.chdir("apps")
        os.mkdir("find")
        with open("file1.txt", "w") as f1:
            f1.write("abc\nadc\nabc\ndef")
        with open("file2.txt", "w") as f2:
            f2.write("file2\ncontent")

    def test_pwd(self):
        output = Pwd().exec()
        stdout = output["stdout"].popleft()

        assert stdout == os.getcwd()

    def test_ls_args(self):
        args = ["", "."]
        stdout1 = list(Ls().exec(args[0])["stdout"])
        stdout2 = list(Ls().exec(args[1])["stdout"])
        print(stdout2)
        assert stdout1 == ["find\n", "file1.txt\n", "file2.txt\n"]
        assert stdout2 == ["find\n", "file1.txt\n", "file2.txt\n"]

    def test_ls_wrong_args(self):
        args = ["", "./doc"]
        output = Ls().exec(args)
        stderr = output["stderr"]
        assert stderr == "Ls: Wrong number of command line arguments"

    def test_ls_wrong_dict(self):
        args = ["/doc"]
        output = Ls().exec(args)
        stderr = output["stderr"]
        assert stderr == f"Ls: {args[0]}: No such directory"

    def test_cat_args(self):
        args = ["file1.txt"]
        output = Cat().exec(args=args)
        stdout = output["stdout"].popleft()

        assert stdout == "abc\nadc\nabc\ndef"

    def test_cat_wrong_args(self):
        args = ["file3.txt"]
        output = Cat().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Cat: {args[0]}: No such file or directory"

    @given(word=st.from_regex(r"[a-z_A-Z]+"))
    def test_cat_stdin(self, word):
        args = []
        stdin = deque()
        stdin.append(word)
        output = Cat().exec(args=args, stdin=stdin)
        stdout = output["stdout"].popleft()
        assert stdout == word

    def test_cd_wrong(self):
        args = ["cd"]
        output = Cd().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Cd: {args[0]}: No such file or directory"

        args = ["cd", "cd"]
        output = Cd().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Cd: Wrong number of command line arguments."

    def test_cd(self):
        os.chdir("..")
        args = ["apps"]
        output = Cd().exec(args=args)
        stdout = output["stdout"]
        assert stdout == deque()

    @given(word=st.from_regex(r"[a-z_A-Z]+"))
    def test_echo(self, word):
        args = [word]
        output = Echo().exec(args=args)
        stdout = output["stdout"].popleft()
        assert stdout == word + "\n"

    def test_head(self):
        args = ["-i", "2", "file1.txt"]
        output = Head().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Wrong Flags"

        args = ["-i", "2"]
        output = Head().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Wrong Flags"

        args = ["-n", "2", "file3.txt"]
        output = Head().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Head: {args[2]}: No such file or directory"

        args = ["file3.txt"]
        output = Head().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Head: {args[0]}: No such file or directory"

        stdin = deque(["abc\n", "adc\n"])
        args = ["-n", "1"]
        output = Head().exec(args=args, stdin=stdin)
        stdout = output["stdout"]

        assert stdout.popleft() == stdin.popleft()

        stdin = deque(["abc\n", "adc\n"])
        args = []
        output = Head().exec(args=args, stdin=stdin)
        stdout = output["stdout"]

        assert list(stdout) == ["abc\n", "adc\n"]

        args = ["-n", "2", "file1.txt"]
        output = Head().exec(args=args)
        stdout = output["stdout"]

        assert list(stdout) == ["abc\n", "adc\n"]

        args = ["file1.txt"]
        output = Head().exec(args=args)
        stdout = output["stdout"]

        assert list(stdout) == ["abc\n", "adc\n", "abc\n", "def"]

    def test_tail(self):
        args = ["-i", "2", "file1.txt"]
        output = Tail().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Wrong Flags"

        args = ["-i", "2"]
        output = Tail().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Wrong Flags"

        args = ["-n", "2", "file3.txt"]
        output = Tail().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Tail: {args[2]}: No such file or directory"

        args = ["file3.txt"]
        output = Tail().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Tail: {args[0]}: No such file or directory"

        stdin = deque(["abc\n", "adc\n"])
        args = ["-n", "1"]
        output = Tail().exec(args=args, stdin=stdin)
        stdout = output["stdout"]

        assert stdout.popleft() == stdin.pop()

        stdin = deque(["abc\n", "adc\n"])
        args = []
        output = Tail().exec(args=args, stdin=stdin)
        stdout = output["stdout"]

        assert list(stdout) == ["abc\n", "adc\n"]

        args = ["-n", "3", "file1.txt"]
        output = Tail().exec(args=args)
        stdout = output["stdout"]

        assert list(stdout) == ["adc\n", "abc\n", "def"]

        args = ["file1.txt"]
        output = Tail().exec(args=args)
        stdout = output["stdout"]

        assert list(stdout) == ["abc\n", "adc\n", "abc\n", "def"]

    def test_Grep(self):
        args = []
        output = Grep().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Grep: Wrong number of command line arguments"

        args = ["a.*?c", "file1.txt"]
        output = Grep().exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["abc\n", "adc\n", "abc\n"]

        args = ["a.*?c", "file1.txt", "file2.txt"]
        output = Grep().exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["file1.txt:abc\n", "file1.txt:adc\n", "file1.txt:abc\n"]

        args = ["AAA", "file3.txt"]
        output = Grep().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Grep: {args[1]}: No such file or directory"

        stdin = deque(["abc\n", "adc\n", "abc\n"])
        args = ["a.*?c"]
        output = Grep().exec(args=args, stdin=stdin)
        stdout = output["stdout"]

        assert list(stdout) == ["abc\n", "adc\n", "abc\n"]

        stdin = deque(["abc\n", "adc\n", "abc\n"])
        args = ["z"]
        output = Grep().exec(args=args, stdin=stdin)
        stdout = output["stdout"]

        assert list(stdout) == []

    def test_Cut(self):
        args = []
        output = Cut().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Cut: Wrong number of command line arguments"

        args = ["-b ", "1,2,3", "file1.txt", "file2.txt"]
        output = Cut().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Cut: Wrong number of command line arguments"

        args = ["-b", "1,2,3", "file3.txt"]
        output = Cut().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Cut: {args[2]}: No such file or directory"

        args = ["-c ", "1,2,3,4", "file1.txt"]
        output = Cut().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Cut: Wrong Flags"

        args = ["-b", "1,3", "file1.txt"]
        output = Cut().exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["ac\n", "ac\n", "ac\n", "df\n"]

        args = ["-b", "1-3", "file1.txt"]
        output = Cut().exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["abc\n", "adc\n", "abc\n", "def\n"]

        args = ["-b", "1-2,3", "file1.txt"]
        output = Cut().exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["abc\n", "adc\n", "abc\n", "def\n"]

        stdin = deque(["abc\n", "adc\n", "abc\n"])
        args = ["-c", "1-2,3"]
        output = Cut().exec(args=args, stdin=stdin)
        stderr = output["stderr"]
        assert stderr == "Cut: Wrong Flags"

        stdin = deque(["abc\n", "adc\n", "abc\n", "deffffff\n"])
        args = ["-b", "1-2,3,5"]
        output = Cut().exec(args=args, stdin=stdin)
        stdout = output["stdout"]
        assert list(stdout) == ["abc\n", "adc\n", "abc\n", "deff\n"]

    def test_Uniq(self):
        args = ["-i ", "file1.txt", "file2.txt"]
        output = Uniq().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Uniq: Wrong number of command line arguments"

        args = ["-i", "file3.txt"]
        output = Uniq().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Uniq: {args[1]}: No such file or directory"

        args = ["file3.txt"]
        output = Uniq().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Uniq: {args[0]}: No such file or directory"

        args = ["-c ", "file1.txt"]
        output = Uniq().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Uniq: Wrong Flags"

        args = ["-i", "file1.txt"]
        output = Uniq().exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["abc\n", "adc\n", "abc\n", "def"]

        args = ["file1.txt"]
        output = Uniq().exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["abc\n", "adc\n", "abc\n", "def"]

        stdin = deque(["abc\n", "abc\n", "adc\n"])
        args = []
        output = Uniq().exec(args=args, stdin=stdin)
        stdout = output["stdout"]
        assert list(stdout) == ["abc\n", "adc\n"]

        stdin = deque(["abc\n", "abc\n", "adc\n"])
        args = ["-i"]
        output = Uniq().exec(args=args, stdin=stdin)
        stdout = output["stdout"]
        assert list(stdout) == ["abc\n", "adc\n"]

    def test_Sort(self):
        args = ["-r ", "file1.txt", "file2.txt"]
        output = Sort().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Sort: Wrong number of command line arguments"

        args = ["-r", "file3.txt"]
        output = Sort().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Sort: {args[1]}: No such file or directory"

        args = ["file3.txt"]
        output = Sort().exec(args=args)
        stderr = output["stderr"]
        assert stderr == f"Sort: {args[0]}: No such file or directory"

        args = ["-i ", "file1.txt"]
        output = Sort().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Sort: Wrong Flags"

        args = ["-r", "file1.txt"]
        output = Sort().exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["def\n", "adc\n", "abc\n", "abc\n"]

        args = ["file1.txt"]
        output = Sort().exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["abc\n", "abc\n", "adc\n", "def\n"]

        stdin = deque(["abc\n", "abc\n", "adc\n"])
        args = []
        output = Sort().exec(args=args, stdin=stdin)
        stdout = output["stdout"]
        assert list(stdout) == ["abc\n", "abc\n", "adc\n"]

        stdin = deque(["abc\n", "abc\n", "adc\n"])
        args = ["-r"]
        output = Sort().exec(args=args, stdin=stdin)
        stdout = output["stdout"]
        assert list(stdout) == ["adc\n", "abc\n", "abc\n"]

    def test_Find(self):
        args = ["-nam", "file1.txt"]
        output = Find().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Find: Wrong Flags"

        args = ["-nam", "file1.txt"]
        output = Find().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Find: Wrong Flags"

        args = [".", "-nam", "file1.txt"]
        output = Find().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Find: Wrong Flags"

        args = [".", "-nam", "file1.txt", "file2.txt"]
        output = Find().exec(args=args)
        stderr = output["stderr"]
        assert stderr == "Find: Wrong number of command line arguments"

        args = ["-name", "file1.txt"]
        output = Find().exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["./file1.txt\n"]

        args = [".", "-name", "file1.txt"]
        output = Find().exec(args=args)
        stdout = output["stdout"]
        print(stdout)
        assert list(stdout) == ["./file1.txt\n"]

        args = ["-name", "file1.txt"]
        output = Find().exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["./file1.txt\n"]

    def test_LocalApp(self):
        args = []
        output = LocalApp("ls").exec(args=args)
        stdout = output["stdout"]
        print(stdout)
        assert list(stdout) == ["file1.txt\nfile2.txt\nfind\n"]

        sys = mock.MagicMock()
        sys.configure_mock(platform="win32")
        print(sys.platform)
        args = []
        output = LocalApp("ls").exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["file1.txt\nfile2.txt\nfind\n"]

    #
    # def test_visit_singlequote_space(self):
    #     i = SingleQuote("  ")
    #     out = self.visitor.visitSingleQuote(i)
    #     self.assertEqual("".join(out["stdout"]), "  ")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_singlequote_disable_doublequote(self):
    #     i = SingleQuote('""')
    #     out = self.visitor.visitSingleQuote(i)
    #     self.assertEqual("".join(out["stdout"]), '""')
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_singlequote_backquote(self):
    #     i = SingleQuote("`echo hello`")
    #     out = self.visitor.visitSingleQuote(i)
    #     self.assertEqual("".join(out["stdout"]), "`echo hello`")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_doublequote_no_substitution(self):
    #     i = DoubleQuote(["a", "b"], False)
    #     out = self.visitor.visitDoubleQuote(i)
    #     self.assertEqual("".join(out["stdout"]), "ab")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_doublequote_has_substitution(self):
    #     i = DoubleQuote(["a", "b", Substitution("echo c")], True)
    #     out = self.visitor.visitDoubleQuote(i)
    #     self.assertEqual("".join(out["stdout"]), "abc")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_doublequote_error_unsafe(self):
    #     i = DoubleQuote(["a", Substitution("_ls a b"), "b"], True)
    #     out = self.visitor.visitDoubleQuote(i)
    #     self.assertEqual("".join(out["stdout"]), "ab")
    #     self.assertEqual(
    #         "".join(out["stderr"]), "wrong number of command line arguments"
    #     )
    #     self.assertNotEquals(out["exit_code"], 0)
    #
    # def test_visit_substitution(self):
    #     i = Substitution("echo foo")
    #     out = self.visitor.visitSub(i)
    #     self.assertEqual("".join(out["stdout"]), "foo")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_substitution_error(self):
    #     i = Substitution("_ls a b")
    #     out = self.visitor.visitSub(i)
    #     self.assertEqual("".join(out["stdout"]), "")
    #     self.assertEqual(
    #         "".join(out["stderr"]), "wrong number of command line arguments"
    #     )
    #     self.assertNotEquals(out["exit_code"], 0)
    #
    # def test_visit_redirectin(self):
    #     i = RedirectIn("file1.txt")
    #     out = self.visitor.visitRedirectIn(i)
    #     self.assertEqual("".join(out["stdout"]), "abc\nadc\nabc\ndef")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_redirectin_glob(self):
    #     i = RedirectIn("*2.txt")
    #     out = self.visitor.visitRedirectIn(i)
    #     self.assertEqual("".join(out["stdout"]), "file2\ncontent")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_redirectin_error(self):
    #     with self.assertRaises(OSError):
    #         self.visitor.visitRedirectIn(RedirectIn("notExist.txt"))
    #
    # def test_visit_redirectout(self):
    #     i = RedirectOut("testRedirectout.txt")
    #     stdin = deque()
    #     stdin.append("aaa\nbbb\nccc")
    #     self.visitor.visitRedirectOut(i, stdin=stdin)
    #     with open("testRedirectout.txt") as f:
    #         lines = f.readlines()
    #     self.assertEqual("".join(lines).strip("\n"), "aaa\nbbb\nccc")
    #     os.remove("testRedirectout.txt")
    #
    # def test_visit_redirectout_error(self):
    #     with self.assertRaises(Exception) as context:
    #         self.visitor.visitRedirectOut(RedirectOut("*.txt"))
    #     self.assertEqual("invalid redirection out", str(context.exception))
    #
    # def test_visit_call_appname_substitution(self):
    #     i = Call(
    #         redirects=[],
    #         appName=Substitution("echo echo"),
    #         args=[["hello world"]],
    #     )
    #     out = self.visitor.visitCall(i)
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "hello world")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_call_appname_substitution_error(self):
    #     i = Call(
    #         redirects=[],
    #         appName=Substitution("cat notExist.txt"),
    #         args=[["hello world"]],
    #     )
    #     with self.assertRaises(Exception) as context:
    #         self.visitor.visitCall(i)
    #     self.assertEqual(
    #         "Cat: notExist.txt: No such file or directory", str(context.exception)
    #     )
    #
    # def test_visit_call_redirectin(self):
    #     i = Call(
    #         redirects=[RedirectIn("file1.txt")],
    #         appName="cat",
    #         args=[],
    #     )
    #     out = self.visitor.visitCall(i)
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "abc\nadc\nabc\ndef")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_call_redirectout_return(self):
    #     i = Call(
    #         redirects=[RedirectOut("testRedirectoutReturn.txt")],
    #         appName="echo",
    #         args=[["call\nredirectout"]],
    #     )
    #     out = self.visitor.visitCall(i)
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     os.remove("testRedirectoutReturn.txt")
    #
    # def test_visit_call_redirection_invalid(self):
    #     i = Call(
    #         redirects=["not redirection type"],
    #         appName="echo",
    #         args=[["call\nredirectout"]],
    #     )
    #     with self.assertRaises(Exception) as context:
    #         self.visitor.visitCall(i)
    #     self.assertEqual("invalid redirections", str(context.exception))
    #
    # def test_visit_call_no_redirectin_but_input(self):
    #     i = Call(
    #         redirects=[],
    #         appName="cat",
    #         args=[],
    #     )
    #     out = self.visitor.visitCall(i, input="input\ncontent")
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "input\ncontent")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_call_redirectin_overwrite_input(self):
    #     with open("testRedirectinOverwriteInput.txt", "w") as f:
    #         f.write("redirectin\ncontent")
    #     i = Call(
    #         redirects=[RedirectIn("testRedirectinOverwriteInput.txt")],
    #         appName="cat",
    #         args=[],
    #     )
    #     out = self.visitor.visitCall(i, input="input\ncontent")
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "redirectin\ncontent")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #     os.remove("testRedirectinOverwriteInput.txt")
    #
    # def test_visit_call_args_doublequote(self):
    #     i = Call(
    #         redirects=[],
    #         appName="echo",
    #         args=[["aa", DoubleQuote(["bb"], False)]],
    #     )
    #     out = self.visitor.visitCall(i)
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "aabb")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_call_args_singlequote(self):
    #     i = Call(
    #         redirects=[],
    #         appName="echo",
    #         args=[["aa"], [SingleQuote("bb")]],
    #     )
    #     out = self.visitor.visitCall(i)
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "aa bb")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_call_args_substitution(self):
    #     i = Call(
    #         redirects=[],
    #         appName="echo",
    #         args=[[Substitution("echo arg_sub_content")]],
    #     )
    #     out = self.visitor.visitCall(i)
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "arg_sub_content")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_call_args_exec_error(self):
    #     i = Call(
    #         redirects=[],
    #         appName="_echo",
    #         args=[[Substitution("cat notExist.txt")]],
    #     )
    #     with self.assertRaises(Exception) as context:
    #         self.visitor.visitCall(i)
    #     self.assertEqual(
    #         "Cat: notExist.txt: No such file or directory", str(context.exception)
    #     )
    #
    # def test_visit_call_args_glob(self):
    #     with open("file3.txt", "w") as f:
    #         f.write("file3\ncontent")
    #     i = Call(
    #         redirects=[],
    #         appName="cat",
    #         args=[["*3.txt"]],
    #     )
    #     out = self.visitor.visitCall(i)
    #     self.assertEqual("".join(out["stdout"]), "file3\ncontent")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #     os.remove("file3.txt")
    #
    # def test_visit_call_args_multiple_glob(self):
    #     i = Call(
    #         redirects=[],
    #         appName="cat",
    #         args=[["*1.txt"], ["*2.txt"]],
    #     )
    #     out = self.visitor.visitCall(i)
    #     self.assertEqual("".join(out["stdout"]), "abc\nadc\nabc\ndeffile2\ncontent")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_seq_left_error_unsafe(self):
    #     i = Seq(
    #         Call(
    #             redirects=[],
    #             appName="_ls",
    #             args=[["notExist"]],
    #         ),
    #         Call(
    #             redirects=[],
    #             appName="echo",
    #             args=[["right\noutput"]],
    #         ),
    #     )
    #     out = self.visitor.visitSeq(i)
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "right\noutput")
    #     self.assertEqual("".join(out["stderr"]), "Ls: notExist: No such directory")
    #     self.assertNotEquals(out["exit_code"], 1)
    #
    # def test_visit_seq_right_error_unsafe(self):
    #     i = Seq(
    #         Call(
    #             redirects=[],
    #             appName="echo",
    #             args=[["left\noutput"]],
    #         ),
    #         Call(
    #             redirects=[],
    #             appName="_ls",
    #             args=[["notExist"]],
    #         ),
    #     )
    #     out = self.visitor.visitSeq(i)
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "left\noutput")
    #     self.assertEqual("".join(out["stderr"]), "Ls: notExist: No such directory")
    #     self.assertNotEquals(out["exit_code"], 1)
    #
    # def test_visit_seq_left_error_right_error_unsafe(self):
    #     i = Seq(
    #         Call(
    #             redirects=[],
    #             appName="_ls",
    #             args=[["notExist1"]],
    #         ),
    #         Call(
    #             redirects=[],
    #             appName="_ls",
    #             args=[["notExist2"]],
    #         ),
    #     )
    #     out = self.visitor.visitSeq(i)
    #     self.assertEqual("".join(out["stdout"]), "")
    #     self.assertEqual(
    #         "".join(out["stderr"]),
    #         "Ls: notExist1: No such directoryLs: notExist2: No such directory",
    #     )
    #     self.assertNotEquals(out["exit_code"], 1)
    #
    # def test_visit_seq_no_error(self):
    #     i = Seq(
    #         Call(
    #             redirects=[],
    #             appName="echo",
    #             args=[["left\noutput"]],
    #         ),
    #         Call(
    #             redirects=[],
    #             appName="echo",
    #             args=[["right\noutput"]],
    #         ),
    #     )
    #     out = self.visitor.visitSeq(i)
    #     self.assertEqual(
    #         "".join(out["stdout"]).strip("\n"), "left\noutput\nright\noutput"
    #     )
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_pipe_with_outleft(self):
    #     i = Pipe(
    #         Call(
    #             redirects=[],
    #             appName="echo",
    #             args=[["left output"]],
    #         ),
    #         Call(
    #             redirects=[],
    #             appName="cut",
    #             args=[["-b"], ["1,2"]],
    #         ),
    #     )
    #     out = self.visitor.visitPipe(i)
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "le")
    #     self.assertEqual("".join(out["stderr"]), "")
    #     self.assertEqual(out["exit_code"], 0)
    #
    # def test_visit_pipe_outright_error_unsafe(self):
    #     i = Pipe(
    #         Call(
    #             redirects=[],
    #             appName="echo",
    #             args=[["notExist"]],
    #         ),
    #         Call(
    #             redirects=[],
    #             appName="_cd",
    #             args=[],
    #         ),
    #     )
    #     out = self.visitor.visitPipe(i)
    #     self.assertEqual("".join(out["stdout"]).strip("\n"), "")
    #     self.assertEqual(
    #         "".join(out["stderr"]), "wrong number of command line arguments"
    #     )
    #     self.assertNotEquals(out["exit_code"], 1)
    #
    def tearDown(self) -> None:
        os.remove("file1.txt")
        os.remove("file2.txt")
        os.rmdir("find")
        os.chdir("..")
        os.rmdir("apps")


if __name__ == "__main__":
    unittest.main()
