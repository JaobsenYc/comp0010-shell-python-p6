import re
import sys
import os
from os import listdir
from collections import deque
from abc import ABC
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
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        stdout.append(os.getcwd())
        std_dict["stdout"] = stdout
        return std_dict


class Cd(Application):
    def exec(self, args, stdin=None):
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        if len(args) == 0 or len(args) > 1:
            std_dict["stderr"] = "Cd: Wrong number of command line arguments."
            std_dict["exit_code"] = "1"
            return std_dict
        try:
            os.chdir(args[0])
        except Exception:
            std_dict["stderr"] = f"Cd: {args[0]}: No such file or directory"
            std_dict["exit_code"] = "1"
            return std_dict
        std_dict["stdout"] = stdout
        return std_dict


class Echo(Application):
    def exec(self, args, stdin=None):
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        # print(args)
        # print(" ".join(args) + "\n"=="".join(args) + "\n")
        # stdout.append(" ".join(args) + "\n")
        stdout.append(" ".join(args) + "\n")
        std_dict["stdout"] = stdout
        return std_dict


class Ls:
    def exec(self, args, stdin=None):
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        if len(args) == 0:
            ls_dir = os.getcwd()
        elif len(args) > 1:
            std_dict["stderr"] = "Ls: Wrong number of command line arguments"
            std_dict["exit_code"] = "1"
            return std_dict
        else:
            ls_dir = args[0]

        try:
            lst_dir = listdir(ls_dir)
        except Exception:
            std_dict["stderr"] = f"Ls: {ls_dir}: No such directory"
            std_dict["exit_code"] = "1"
            return std_dict
        for f in lst_dir:
            if not f.startswith("."):
                stdout.append(f + "\n")
        std_dict["stdout"] = stdout
        return std_dict


class Cat:
    def exec(self, args, stdin=None):
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        if not stdin:
            for a in args:
                try:
                    lines = self.file_helper(a)
                    stdout.append(lines)
                except FileNotFoundError:
                    std_dict["stderr"] = f"Cat: {a}: No such file or directory"
                    std_dict["exit_code"] = "1"
                    return std_dict

        else:
            stdout = stdin

        std_dict["stdout"] = stdout
        return std_dict

    def file_helper(self, file):
        with open(file) as f:
            lines = f.read()
        return lines


class Head:
    def exec(self, args, stdin=None):
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        num_lines = 10
        if len(args) == 1:
            num_lines = 10
            file = args[0]
            try:
                lines = self.file_helper(file)
            except FileNotFoundError:
                std_dict["stderr"] = f"Head: {file}: No such file or directory"
                std_dict["exit_code"] = "1"
                return std_dict
        elif len(args) == 2:
            if args[0] != "-n":
                std_dict["stderr"] = "Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
            else:
                num_lines = int(args[1])
                lines = list(stdin)
        elif len(args) == 3:
            if args[0] != "-n":
                std_dict["stderr"] = "Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
            else:
                num_lines = int(args[1])
                file = args[2]
            try:
                lines = self.file_helper(file)
            except FileNotFoundError:
                std_dict["stderr"] = f"Head: {file}: No such file or directory"
                std_dict["exit_code"] = "1"
                return std_dict
        else:
            lines = list(stdin)

        stdout = self.helper(lines, num_lines)
        std_dict["stdout"] = stdout
        return std_dict

    def file_helper(self, file):
        with open(file) as f:
            lines = f.readlines()
        return lines

    def helper(self, lines, num_lines):
        output = deque()
        display_length = min(len(lines), int(num_lines))
        for i in range(0, display_length):
            output.append(lines[i])
        return output


class Tail:
    def exec(self, args, stdin=None):
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        num_lines = 10
        if len(args) == 1:
            num_lines = 10
            file = args[0]
            try:
                lines = self.file_helper(file)
            except FileNotFoundError:
                std_dict["stderr"] = f"Tail: {file}: No such file or directory"
                std_dict["exit_code"] = "1"
                return std_dict
        elif len(args) == 2:
            if args[0] != "-n":
                std_dict["stderr"] = "Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
            else:
                num_lines = int(args[1])
                lines = list(stdin)
        elif len(args) == 3:
            if args[0] != "-n":
                std_dict["stderr"] = "Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
            else:
                num_lines = int(args[1])
                file = args[2]
            try:
                lines = self.file_helper(file)
            except FileNotFoundError:
                std_dict["stderr"] = f"Tail: {file}: No such file or directory"
                std_dict["exit_code"] = "1"
                return std_dict
        else:
            lines = list(stdin)

        stdout = self.helper(lines, num_lines)

        std_dict["stdout"] = stdout
        return std_dict

    def file_helper(self, file):
        with open(file) as f:
            lines = f.readlines()
        return lines

    def helper(self, lines, num_lines):
        output = deque()
        display_length = min(len(lines), num_lines)
        for i in range(0, min(len(lines), num_lines)):
            output.append(lines[len(lines) - display_length + i])
        return output


class Grep:
    def exec(self, args, stdin=None):
        # print("args: ", args)
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        if len(args) < 1:
            std_dict["stderr"] = "Grep: Wrong number of command line arguments"
            std_dict["exit_code"] = "1"
            return std_dict
        elif len(args) > 1:
            pattern = args[0]
            files = args[1:]
            for file in files:
                try:
                    lines = self.file_helper(file)
                    for line in lines:
                        if re.match(pattern, line):
                            if len(files) > 1:
                                stdout.append(f"{file}:{line}")
                            else:
                                stdout.append(line)
                except FileNotFoundError:
                    errMessage = f"Grep: {file}: No such file or directory"
                    std_dict["stderr"] = errMessage
                    std_dict["exit_code"] = "1"
                    return std_dict
            std_dict["stdout"] = stdout
            return std_dict
        else:
            pattern = args[0]
            input = list(stdin)
            for line in input:
                if re.match(pattern, line):
                    stdout.append(line)
            std_dict["stdout"] = stdout
            return std_dict

    def file_helper(self, file):
        with open(file) as f:
            lines = f.readlines()
        return lines


class Cut:
    def exec(self, args, stdin=None):
        lines = None
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        if len(args) > 3:
            std_dict["stderr"] = "Cut: Wrong number of command line arguments"
            std_dict["exit_code"] = "1"
            return std_dict
        elif len(args) == 3:
            if args[0] != "-b":
                std_dict["stderr"] = "Cut: Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
            pattern = args[1]
            file = args[2]

        else:
            if args:
                if args[0] != "-b":
                    std_dict["stderr"] = "Cut: Wrong Flags"
                    std_dict["exit_code"] = "1"
                    return std_dict
                pattern = args[1]
                input = list(stdin)
                lines = []

                [lines.extend(i.splitlines()) for i in input]
            else:
                err = "Cut: Wrong number of command line arguments"
                std_dict["stderr"] = err
                std_dict["exit_code"] = "1"
                return std_dict

        pattern_list = pattern.split(",")

        if not lines:
            try:
                lines = self.file_helper(file)

            except FileNotFoundError:
                std_dict["stderr"] = f"Cut: {file}: No such file or directory"
                std_dict["exit_code"] = "1"
                return std_dict
                # If the cut command uses the -b option,
                # then cut will sort all the positions
                # after -b from small to large, and then
                # extract them.

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

        std_dict["stdout"] = stdout
        return std_dict

    def file_helper(self, file):
        with open(file) as f:
            lines = f.read().splitlines()

        return lines


class Uniq:
    def exec(self, args, stdin=None):
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        ignore = False

        if len(args) > 2:
            std_dict["stderr"] = "Uniq: Wrong number of command line arguments"
            std_dict["exit_code"] = "1"
            return std_dict
        elif len(args) == 2:
            if args[0] != "-i":
                std_dict["stderr"] = "Uniq: Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
            else:
                ignore = True
            file = args[1]
            try:
                stdout = self.file_helper(file, ignore)
                std_dict["stdout"] = stdout
            except FileNotFoundError:
                std_dict["stderr"] = f"Uniq: {file}: No such file or directory"
                std_dict["exit_code"] = "1"
            return std_dict
        elif len(args) == 1:
            if args[0] != "-i":
                file = args[0]
                try:
                    stdout = self.file_helper(file, ignore)
                    std_dict["stdout"] = stdout
                except FileNotFoundError:
                    errMessage = f"Uniq: {file}: No such file or directory"
                    std_dict["stderr"] = errMessage
                    std_dict["exit_code"] = "1"
                return std_dict
            else:
                ignore = True

        input = list(stdin)
        lines = []

        [lines.extend(i.splitlines(True)) for i in input]
        stdout = self.helper(ignore, lines)
        std_dict["stdout"] = stdout
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
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        if len(args) > 2:
            std_dict["stderr"] = "Sort: Wrong number of command line arguments"
            std_dict["exit_code"] = "1"
            return std_dict
        elif len(args) == 2:
            if args[0] != "-r":
                std_dict["stderr"] = "Sort: Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
            else:
                reverse = True
            file = args[1]

            try:
                stdout = self.file_helper(file, reverse)
                std_dict["stdout"] = stdout
            except FileNotFoundError:
                std_dict["stderr"] = f"Sort: {file}: No such file or directory"
                std_dict["exit_code"] = "1"
            return std_dict

        elif len(args) == 1:
            if args[0] != "-r":
                file = args[0]
                try:
                    stdout = self.file_helper(file, reverse)
                    std_dict["stdout"] = stdout
                except FileNotFoundError:
                    errMessage = f"Sort: {file}: No such file or directory"
                    std_dict["stderr"] = errMessage
                    std_dict["exit_code"] = "1"
                return std_dict
            else:
                reverse = True
        lines = []
        input = list(stdin)
        [lines.extend(i.splitlines()) for i in input]
        stdout = self.helper(lines, reverse)
        std_dict["stdout"] = stdout
        return std_dict

    def file_helper(self, file, reverse):
        with open(file) as f:
            lines = f.read().splitlines()
            output = self.helper(lines, reverse)
        return output

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
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        if len(args) > 3:
            std_dict["stderr"] = "Find: Wrong number of command line arguments"
            std_dict["exit_code"] = "1"
            return std_dict
        elif len(args) == 3:
            if args[1] != "-name":
                std_dict["stderr"] = "Find: Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
            pattern = args[2]
            dict = args[0]
        else:
            if args[0] != "-name":
                std_dict["stderr"] = "Find: Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
            pattern = args[1]
            dict = "."

        res = self.helper(pattern, [dict], [])
        for i in res:
            stdout.append(i + "\n")

        std_dict["stdout"] = stdout
        return std_dict

    def helper(self, pattern, stack, res):
        while stack:

            current = stack.pop()
            dirs = os.listdir(current)

            for d in dirs:
                d1 = os.path.join(current, d)
                if not os.path.isdir(d1):
                    if fnmatch.fnmatch(d, pattern):
                        res.append("/".join([current, d]))

                else:
                    stack.append("/".join([current, d]))

        return res


#
# class NotSupported:
#     def __init__(self, app_token):
#         self.app_token = app_token
#
#     def exec(self, out, args):
#         raise ValueError(f"unsupported application {self.app_token}")


class LocalApp:
    def __init__(self, appName):
        self.app = appName

    def _getApp(self):
        app = self.app
        assert app is not None and type(app) == str
        # is path
        if os.path.dirname(app):
            # path exists,is accessible, and not a directory
            if self._is_valid_path_to_executable(self.app) is not None:
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

        # windows has to check file extension
        possibleExecutable = self._get_system_executables(app, path)

        for p in path:
            for executable in possibleExecutable:
                executablePath = os.path.join(os.path.normcase(p), executable)
                if self._is_valid_path_to_executable(executablePath) is not None:
                    return executablePath

    def _get_system_executables(self, app, path):
        possibleExecutable = [app]
        if sys.platform == "win32":
            if os.curdir not in path:
                # add current directory to path so
                # applications are found in current dir
                path.append(os.curdir)

            pathExtensions = os.getenv("PATHEXT").split(os.pathsep)
            pathExtensionList = [e for e in pathExtensions if e is not None]

            possibleExecutable = self._get_possible_executable(app, pathExtensionList)
        return possibleExecutable

    def _get_possible_executable(self, app, pathExtensionList):
        for extension in pathExtensionList:
            if app.lower().endswith(extension.lower()):
                possibleExecutable = [app]
                break
        else:
            possibleExecutable = [app + extension for extension in pathExtensionList]

        return possibleExecutable

    def _is_valid_path_to_executable(
        self, executablePath, existsAndExecutable=os.F_OK | os.X_OK
    ):
        if (
            os.path.exists(executablePath)
            and os.access(executablePath, existsAndExecutable)
            and not os.path.isdir(executablePath)
        ):
            return executablePath
        else:
            return None

    def exec(self, args=[], stdin=deque()):
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        assert type(stdin) == deque and type(args) == list
        sysApp = self._getApp()
        if sysApp is not None:
            stdin = "".join(stdin)
            args = [sysApp] + args
            if len(stdin) > 0:
                process = Popen(
                    args,
                    universal_newlines=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                )
                output, error = process.communicate(stdin)
            else:
                process = Popen(
                    args,
                    universal_newlines=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                output, error = process.communicate()
            if error != "":
                raise Exception(f"{self.app}: " + error)
            else:
                stdout.append(output)
        else:
            std_dict["stderr"].append(f"No application {self.app} is found\n")
        std_dict["stdout"] = stdout
        return std_dict


# os.mkdir("apps")
# os.chdir("apps")
# with open("file1.txt", "w") as f1:
#     f1.write("abc\nadc\nabc\ndef")
#
# with open("file2.txt", "w") as f2:
#     f2.write("file2\ncontent")
#
#
# args = []
# output = LocalApp("ls").exec(args=args)
# stdout = output["stdout"]
#
#
# os.remove("file1.txt")
# os.remove("file2.txt")
# os.chdir("..")
# os.rmdir("apps")
# print(stdout)
