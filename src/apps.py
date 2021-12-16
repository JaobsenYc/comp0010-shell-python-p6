import re
import sys
import os
from os import listdir
from collections import deque
from abc import ABC, abstractmethod
import fnmatch
import itertools
import subprocess
from subprocess import Popen


class Application(ABC):
    @classmethod
    def exec(self, args, stdin):
        raise (Exception(NotImplementedError))


class Pwd(Application):
    def exec(self, args=None, stdin=None):
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        stdout.append(os.getcwd())
        std_dict['stdout'] = stdout
        return std_dict


class Cd(Application):
    def exec(self, args, stdin=None):
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        if len(args) == 0 or len(args) > 1:
            std_dict['stderr'] = "wrong number of command line arguments"
            std_dict['exit_code'] = "1"
            return std_dict
        os.chdir(args[0])

        std_dict['stdout'] = stdout
        return std_dict
        # print("apps/Cd: " + os.getcwd())


class Echo(Application):
    def exec(self, args, stdin=None):
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        # print(args)
        # print(" ".join(args) + "\n"=="".join(args) + "\n")
        # stdout.append(" ".join(args) + "\n")
        stdout.append(" ".join(args) + "\n")
        std_dict['stdout'] = stdout
        return std_dict


class Ls:
    def exec(self, args, stdin=None):
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        if len(args) == 0:
            ls_dir = os.getcwd()
        elif len(args) > 1:
            std_dict['stderr'] = "wrong number of command line arguments"
            std_dict['exit_code'] = "1"
            return std_dict
        else:
            ls_dir = args[0]
        for f in listdir(ls_dir):
            if not f.startswith("."):
                stdout.append(f + "\n")
        std_dict['stdout'] = stdout
        return std_dict


class Cat:
    def exec(self, args, stdin=None):
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        if stdin:
            stdout = stdin

        else:
            for a in args:
                with open(a) as f:
                    stdout.append(f.read())

        std_dict['stdout'] = stdout
        return std_dict


class Head:
    def exec(self, args, stdin=None):
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        num_lines = 10
        if len(args) == 1:
            num_lines = 10
            file = args[0]
            with open(file) as f:
                lines = f.readlines()
        elif len(args) == 2:
            if args[0] != "-n":
                std_dict['stderr'] = "wrong flags"
                std_dict['exit_code'] = "1"
                return std_dict
            else:
                num_lines = int(args[1])
                lines = list(stdin)
        elif len(args) == 3:
            if args[0] != "-n":
                std_dict['stderr'] = "wrong flags"
                std_dict['exit_code'] = "1"
                return std_dict
            else:
                num_lines = int(args[1])
                file = args[2]
            with open(file) as f:
                lines = f.readlines()
        else:
            lines = list(stdin)

        stdout = self.helper(lines, num_lines)

        std_dict['stdout'] = stdout
        return std_dict

    def helper(self, lines, num_lines):
        output = deque()
        display_length = min(len(lines), int(num_lines))
        for i in range(0, display_length):
            output.append(lines[i])
        return output


class Tail:
    def exec(self, args, stdin=None):
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        num_lines = 10
        if len(args) == 1:
            num_lines = 10
            file = args[0]
            with open(file) as f:
                lines = f.readlines()
        elif len(args) == 2:
            if args[0] != "-n":
                std_dict['stderr'] = "wrong flags"
                std_dict['exit_code'] = "1"
                return std_dict
            else:
                num_lines = int(args[1])
                lines = list(stdin)
        elif len(args) == 3:
            if args[0] != "-n":
                std_dict['stderr'] = "wrong flags"
                std_dict['exit_code'] = "1"
                return std_dict
            else:
                num_lines = int(args[1])
                file = args[2]
            with open(file) as f:
                lines = f.readlines()
        else:
            lines = list(stdin)

        stdout = self.helper(lines, num_lines)

        std_dict['stdout'] = stdout
        return std_dict

    def helper(self, lines, num_lines):
        output = deque()
        display_length = min(len(lines), num_lines)
        for i in range(0, min(len(lines), num_lines)):
            output.append(lines[len(lines) - display_length + i])
        return output


class Grep:
    def exec(self, args, stdin=None):
        # print("args: ", args)
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        if len(args) < 1:
            std_dict['stderr'] = "wrong number of command line arguments"
            std_dict['exit_code'] = "1"
            return std_dict
        elif len(args) > 1:
            pattern = args[0]
            files = args[1:]
            for file in files:
                with open(file) as f:
                    lines = f.readlines()
                    for line in lines:
                        if re.match(pattern, line):
                            if len(files) > 1:
                                stdout.append(f"{file}:{line}")
                            else:
                                stdout.append(line)
            std_dict['stdout'] = stdout
            return std_dict
        else:
            pattern = args[0]
            input = list(stdin)
            for line in input:
                if re.match(pattern, line):
                    stdout.append(line)
            std_dict['stdout'] = stdout
            return std_dict


class Cut:
    def exec(self, args, stdin=None):
        lines = None
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        if len(args) > 3:
            std_dict['stderr'] = "wrong number of command line arguments"
            std_dict['exit_code'] = "1"
            return std_dict
        elif len(args) == 3:
            if args[0] != "-b":
                std_dict['stderr'] = "wrong flags"
                std_dict['exit_code'] = "1"
                return std_dict
            pattern = args[1]
            file = args[2]
        else:
            if args[0] != "-b":
                std_dict['stderr'] = "wrong flags"
                std_dict['exit_code'] = "1"
                return std_dict
            pattern = args[1]
            input = stdin.pop()
            lines = [input.strip()]

        pattern_list = pattern.split(",")
        if not lines:
            with open(file) as f:
                # If the cut command uses the -b option, then when executing this command,
                # cut will sort all the positions after -b from small to large, and then extract them.
                lines = f.read().splitlines()

        for line in lines:
            start_list = []
            end_list = []
            byte_list = []
            cut_line = ""
            for p in pattern_list:
                if "-" in p:
                    start_i, end_i = p.split("-")
                    start_i = 1 if start_i == "" else int(start_i)
                    end_i = len(line) if end_i == "" else int(end_i)
                    start_list.append(int(start_i) - 1)
                    end_list.append(int(end_i) - 1)
                else:
                    byte_list.append(int(p) - 1)
            for i in range(len(line)):
                if i in byte_list:
                    cut_line += line[i]
                else:
                    for j in range(len(start_list)):
                        if i >= start_list[j] and i <= end_list[j]:
                            cut_line += line[i]
                            break

            stdout.append(cut_line + "\n")

        std_dict['stdout'] = stdout
        return std_dict


class Uniq:
    def exec(self, args, stdin=None):
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        ignore = False

        if len(args) > 2:
            std_dict['stderr'] = "wrong number of command line arguments"
            std_dict['exit_code'] = "1"
            return std_dict
        elif len(args) == 2:
            if args[0] != "-i":
                std_dict['stderr'] = "wrong flags"
                std_dict['exit_code'] = "1"
                return std_dict
            else:
                ignore = True
            file = args[1]
            stdout = self.file_helper(file, ignore)
            std_dict['stdout'] = stdout
            return std_dict
        elif len(args) == 1:
            if args[0] != "-i":
                file = args[0]
                stdout = self.file_helper(file, ignore)
                std_dict['stdout'] = stdout
                return std_dict
            else:
                ignore = True

        input = list(stdin)
        lines = []

        # for i in input:
        #     line=i.splitlines(True)
        #     for j in line:
        #         lines.append(j)

        [lines.extend(i.splitlines(True)) for i in input]

        stdout = self.helper(ignore, lines)
        std_dict['stdout'] = stdout
        return std_dict

    def file_helper(self, file, ignore):
        with open(file) as f:
            lines = f.readlines()
            output = self.helper(ignore, lines)
        return output

    def helper(self, ignore, lines):
        result = deque()
        output = (
            [k for k, g in itertools.groupby(lines)]
            if not ignore
            else [
                n
                for i, n in enumerate(lines)
                if i == 0 or n.casefold() != lines[i - 1].casefold()
            ]
        )
        for i in output:
            result.append(i)
        return result


class Sort:
    def exec(self, args, stdin=None):
        reverse = False
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        if len(args) > 2:
            std_dict['stderr'] = "wrong number of command line arguments"
            std_dict['exit_code'] = "1"
            return std_dict
        elif len(args) == 2:
            if args[0] != "-r":
                std_dict['stderr'] = "wrong flags"
                std_dict['exit_code'] = "1"
                return std_dict
            else:
                reverse = True
            file = args[1]
            with open(file) as f:
                lines = f.read().splitlines()
                stdout = self.helper(lines, reverse)
                std_dict['stdout'] = stdout
                return std_dict
        elif len(args) == 1:
            if args[0] != "-r":
                file = args[0]
                with open(file) as f:
                    lines = f.read().splitlines()
                    stdout = self.helper(lines, reverse)
                std_dict['stdout'] = stdout
                return std_dict
            else:
                reverse = True
        lines = []
        input = list(stdin)
        [lines.extend(i.splitlines()) for i in input]
        stdout = self.helper(lines, reverse)
        std_dict['stdout'] = stdout
        return std_dict

    def helper(self, lines, reverse):
        output = deque()
        lines.sort()
        if reverse:
            lines.reverse()
            for i in lines:
                output.append(i + "\n")
        else:
            for i in lines:
                output.append(i + "\n")
        return output


class Find:
    def exec(self, args, stdin=None):
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        if len(args) > 3:
            std_dict['stderr'] = "wrong number of command line arguments"
            std_dict['exit_code'] = "1"
            return std_dict
        elif len(args) == 3:
            if args[1] != "-name":
                std_dict['stderr'] = "wrong flags"
                std_dict['exit_code'] = "1"
                return std_dict
            pattern = args[2]
            dict = args[0]
        else:
            if args[0] != "-name":
                std_dict['stderr'] = "wrong flags"
                std_dict['exit_code'] = "1"
                return std_dict
            pattern = args[1]
            dict = "."

        res = self.helper(pattern, [dict], [])
        for i in res:
            stdout.append(i + "\n")

        std_dict['stdout'] = stdout
        return std_dict

    def helper(self, pattern, stack, res):
        while stack:

            current = stack.pop()
            dirs = os.listdir(current)
            # print(current, dirs)

            for d in dirs:
                d1 = os.path.join(current, d)
                if not os.path.isdir(d1):
                    if fnmatch.fnmatch(d, pattern):
                        res.append("/".join([current, d]))
                elif os.path.isdir(d1):
                    stack.append("/".join([current, d]))

        return res


class NotSupported:
    def __init__(self, app_token):
        self.app_token = app_token

    def exec(self, out, args):
        raise ValueError(f"unsupported application {self.app_token}")


class LocalApp:
    def __init__(self, appName):
        self.app = appName

    def _getApp(self):
        app = self.app
        existsAndExecutable = os.F_OK | os.X_OK
        # is path
        if os.path.dirname(app):
            # path exists,is accessible, and not a directory
            if (
                    os.path.exists(app)
                    and os.access(app, existsAndExecutable)
                    and not os.path.isdir(app)
            ):
                return self.app
            return None

        # get a mess of concatenated system path
        path = os.environ.get("PATH", None)
        if path is None:
            return None

        # Match file system encoding
        path = os.fsdecode(path)
        # Split each path into a list
        path = path.split(os.pathsep)

        possibleExecutable = [app]
        # windows has to check file extension
        if sys.platform == "win32":
            if os.curdir not in path:
                # add current directory to path so applications are found in current dir
                path.append(os.curdir)

            pathExtensions = os.getenv("PATHEXT").split(os.pathsep)
            pathExtensionList = [
                extension for extension in pathExtensions if extension is not None
            ]

            for extension in pathExtensionList:
                if app.lower().endswith(extension.lower()):
                    possibleExecutable = [app]
                    break
            else:
                possibleExecutable = [
                    app + extension for extension in pathExtensionList
                ]

        for p in path:
            for executable in possibleExecutable:
                executablePath = os.path.join(os.path.normcase(p), executable)
                if (
                        os.path.exists(executablePath)
                        and os.access(executablePath, existsAndExecutable)
                        and not os.path.isdir(executablePath)
                ):
                    return executablePath

    def exec(self, args, stdin=None):
        std_dict = {'stdout': deque(), 'stderr': deque(), 'exit_code': 0}
        stdout = deque()
        sysApp = self._getApp()
        if sysApp is not None:
            process = Popen(
                f"{sysApp} {' '.join(args)}",
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            output, error = process.communicate(input=stdin)
            if error != "":
                raise Exception(error)
            else:
                stdout.append(output)
        else:
            raise Exception(f"No application {app} is found")
        std_dict['stdout'] = stdout
        return std_dict


if __name__ == "__main__":
    # print("Pwd", Pwd().exec())
    # print("Ls", Ls().exec(args=[]))
    # print("Ls", Ls().exec(args=["F:\\OneDrive\\OneDrive - University College London\\"]))
    # print("Cat", Cat().exec(args=["dir1/file1.txt"]))
    # print("Grep", Grep().exec(args=['A..', "dir1/file1.txt"]))
    # print("Head", Head().exec(args=["-n", 3, "file.txt"]))
    # print("Tail", Tail().exec(args=["-n", 3, "test.txt"]))
    # print("Echo", Echo().exec(args=["echo hello world"]))
    # print("Find local", Find().exec(args=["-name", "parsercombinator.*"]))
    # print("Find local", Find().exec(args=["dir1", "-name", "*.txt"]))
    # print("Find local", Find().exec(args=["dir1", "-name", "*.txt"]))
    # print("Cut file", Cut().exec(args=["-b", '-2'], stdin="abc"))
    # print("Cut file", Cut().exec(args=["-b", '-2', "dir/file1.txt"]))
    # print("Uniq Care case", Uniq().exec(args=['test_abc.txt']))
    # print("Uniq Ignore case", Uniq().exec(args=["-i", 'test_abc.txt']))
    # print("Uniq Care case", Uniq().exec(args=['test_abc.txt']))
    # print("Uniq Ignore case", Uniq().exec(args=["-i"], stdin='test_abc.txt'))
    # print("Sort", Sort().exec(args=['dir1/file1.txt']))
    # args_num = len(sys.argv) - 1
    # if args_num > 0:
    #     if args_num != 2:
    #         raise ValueError("wrong number of command line arguments")
    #     if sys.argv[1] != "-c":
    #         raise ValueError(f"unexpected command line argument {sys.argv[1]}")
    #     out = deque()
    #     print(out)
    #     # eval(sys.argv[2], out)
    #     while len(out) > 0:
    #         print(out.popleft(), end="")
    # else:
    #     while True:
    #         print(os.getcwd() + "> ", end="")
    #         cmdline = input()
    #         out = deque()
    #         print(cmdline,out)
    #         # eval(cmdline, out)
    #         while len(out) > 0:
    #             print(out.popleft(), end="")
