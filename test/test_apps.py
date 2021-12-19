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
        assert sorted(stdout1) == sorted(["find\n", "file1.txt\n", "file2.txt\n"])
        assert sorted(stdout2) == sorted(["find\n", "file1.txt\n", "file2.txt\n"])

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
        assert list(stdout) == ["file1.txt\nfile2.txt\nfind\n"]

        args = []
        stdin = deque(["abc\n", "abc\n", "adc\n"])
        output = LocalApp("echo").exec(args=args, stdin=stdin)
        stdout = output["stdout"]
        print(output)
        assert list(stdout) == ['\n']

        args = []
        app_name = "osss"
        output = LocalApp(app_name).exec(args=args)
        stderr = output["stderr"]

        assert stderr == f"No application {app_name} is found\n"

        sys = mock.MagicMock()
        sys.configure_mock(platform="win32")
        args = []
        output = LocalApp("ls").exec(args=args)
        stdout = output["stdout"]
        assert list(stdout) == ["file1.txt\nfile2.txt\nfind\n"]



    def tearDown(self) -> None:
        os.remove("file1.txt")
        os.remove("file2.txt")
        os.rmdir("find")
        os.chdir("..")
        os.rmdir("apps")


if __name__ == "__main__":
    unittest.main()
