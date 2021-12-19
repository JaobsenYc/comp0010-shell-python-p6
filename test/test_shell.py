import unittest
import mock
import subprocess


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
        with mock.patch("builtins.input", return_value='-c echo "hello world"'):
            self.assertEqual(self.eval("")[0].strip(), "hello world")

    # has been covered
    def test_shell_handle_two_args(self):
        pass

    def test_shell_handle_wrong_num_arg(self):
        out, err = self.eval("-d", 'echo "hello world"')
        print(out, err)
        assert len(err) > 0

    def test_shell_handle_unexpected_arg(self):
        out, err = self.eval("-d", 'echo "hello world"')
        print(out, err)
        assert len(out) > 0


if __name__ == "__main__":
    unittest.main()
