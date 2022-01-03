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
    """Abstract Base Classes of Application"""

    @classmethod
    def exec(cls, args, stdin):
        raise (Exception(NotImplementedError))


class Pwd(Application):
    """Outputs the current working directory followed by a newline."""

    def exec(self, args=None, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        stdout.append(os.getcwd())
        std_dict["stdout"] = stdout
        return std_dict


class Cd(Application):
    """Changes the current working directory."""

    def exec(self, args, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
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
    """
    Prints its arguments separated by spaces and followed by a newline to stdout
    """

    def exec(self, args, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        # print(args)
        # print(" ".join(args) + "\n"=="".join(args) + "\n")
        # stdout.append(" ".join(args) + "\n")
        stdout.append(" ".join(args) + "\n")
        std_dict["stdout"] = stdout
        return std_dict


class Ls:
    """
    Lists the content of a directory.
    It prints a list of files and directories separated by tabs and followed by a newline.
    Ignores files and directories whose names start with `.`.
    """

    def exec(self, args, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
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
        for file in lst_dir:
            if not file.startswith("."):
                stdout.append(file + "\n")
        std_dict["stdout"] = stdout
        return std_dict


class Cat:
    """
    Concatenates the content of given files and prints it to stdout
    """

    def exec(self, args, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
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

    @classmethod
    def file_helper(cls, file):
        with open(file) as f:
            lines = f.read()
        return lines


class Head:
    """
    Prints the first N lines of a given file or stdin.
    If there are less than N lines, prints only the existing lines without raising an exception.
    """

    def exec(self, args, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
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
            if args[0] == "-n":
                num_lines = int(args[1])
                lines = list(stdin)
            else:
                std_dict["stderr"] = "Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict

        elif len(args) == 3:
            if args[0] == "-n":
                num_lines = int(args[1])
                file = args[2]
            else:
                std_dict["stderr"] = "Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
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

    @classmethod
    def file_helper(cls, file):
        with open(file, "r") as f:
            lines = f.readlines()
        return lines

    @classmethod
    def helper(cls, lines, num_lines):
        output = deque()
        display_length = min(len(lines), int(num_lines))
        for i in range(0, display_length):
            output.append(lines[i])
        return output


class Tail:
    """
    Prints the last N lines of a given file or stdin.
    If there are less than N lines, prints only the existing lines without raising an exception.
    """

    def exec(self, args, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
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
            if args[0] == "-n":
                num_lines = int(args[1])
                lines = list(stdin)
            else:
                std_dict["stderr"] = "Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict

        elif len(args) == 3:
            if args[0] == "-n":
                num_lines = int(args[1])
                file = args[2]

            else:
                std_dict["stderr"] = "Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
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

    @classmethod
    def file_helper(cls, file):
        with open(file, "r") as f:
            lines = f.readlines()
        return lines

    @classmethod
    def helper(cls, lines, num_lines):
        output = deque()
        display_length = min(len(lines), num_lines)
        for i in range(0, min(len(lines), num_lines)):
            output.append(lines[len(lines) - display_length + i])
        return output


class Grep:
    """
    Searches for lines containing a match to the specified pattern.
    The output of the command is the list of lines. Each line is printed followed by a newline.
    """

    def exec(self, args, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        if len(args) < 1:
            std_dict["stderr"] = "Grep: Wrong number of command line arguments"
            std_dict["exit_code"] = "1"
            return std_dict
        if len(args) > 1:
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
                    std_dict["stderr"] = f"Grep: {file}: No such file or directory"
                    std_dict["exit_code"] = "1"
                    return std_dict
            std_dict["stdout"] = stdout
            return std_dict

        pattern = args[0]
        for line in list(stdin):
            if re.match(pattern, line):
                stdout.append(line)
        std_dict["stdout"] = stdout
        return std_dict

    @classmethod
    def file_helper(cls, file):
        with open(file, "r") as f:
            lines = f.readlines()
        return lines


class Cut:
    """
    Cuts out sections from each line of a given file or stdin and prints the result to stdout.
    """

    def exec(self, args, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
        lines = None
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        if len(args) > 3:
            std_dict["stderr"] = "Cut: Wrong number of command line arguments"
            std_dict["exit_code"] = "1"
            return std_dict
        if len(args) == 3:
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

        stdout = self.cut_helper(lines, pattern_list)
        std_dict["stdout"] = stdout
        return std_dict

    @classmethod
    def cut_helper(cls, lines, pattern_list):
        result = deque()
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
                        if start_list[j] <= i <= end_list[j]:
                            cut_line += line[i]
                            break
            result.append(cut_line + "\n")
        return result

    @classmethod
    def file_helper(cls, file):
        with open(file, "r") as f:
            lines = f.read().splitlines()

        return lines


class Uniq:
    """
    Detects and deletes adjacent duplicate lines from an input file/stdin and prints the result to stdout.
    """

    def exec(self, args, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        ignore = False

        if len(args) > 2:
            std_dict["stderr"] = "Uniq: Wrong number of command line arguments"
            std_dict["exit_code"] = "1"
            return std_dict
        if len(args) == 2:
            if args[0] == "-i":
                ignore = True
            else:
                std_dict["stderr"] = "Uniq: Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
            file = args[1]
            try:
                stdout = self.file_helper(file, ignore)
                std_dict["stdout"] = stdout
            except FileNotFoundError:
                std_dict["stderr"] = f"Uniq: {file}: No such file or directory"
                std_dict["exit_code"] = "1"
            return std_dict
        if len(args) == 1:
            if args[0] == "-i":
                ignore = True
            else:
                file = args[0]
                try:
                    stdout = self.file_helper(file, ignore)
                    std_dict["stdout"] = stdout
                except FileNotFoundError:
                    errMessage = f"Uniq: {file}: No such file or directory"
                    std_dict["stderr"] = errMessage
                    std_dict["exit_code"] = "1"
                return std_dict

        lines = []
        [lines.extend(i.splitlines(True)) for i in list(stdin)]
        stdout = self.helper(ignore, lines)
        std_dict["stdout"] = stdout
        return std_dict

    @classmethod
    def file_helper(cls, file, ignore):
        with open(file, "r") as f:
            lines = f.readlines()
            output = cls.helper(ignore, lines)
        return output

    @classmethod
    def helper(cls, ignore, lines):
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
    """
    Sorts the contents of a file/stdin line by line and prints the result to stdout.
    """

    def exec(self, args, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
        reverse = False
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        if len(args) > 2:
            std_dict["stderr"] = "Sort: Wrong number of command line arguments"
            std_dict["exit_code"] = "1"
            return std_dict
        if len(args) == 2:
            if args[0] == "-r":
                reverse = True
            else:
                std_dict["stderr"] = "Sort: Wrong Flags"
                std_dict["exit_code"] = "1"
                return std_dict
            file = args[1]

            try:
                stdout = self.file_helper(file, reverse)
                std_dict["stdout"] = stdout
            except FileNotFoundError:
                std_dict["stderr"] = f"Sort: {file}: No such file or directory"
                std_dict["exit_code"] = "1"
            return std_dict

        if len(args) == 1:
            if args[0] == "-r":
                reverse = True
            else:
                file = args[0]
                try:
                    stdout = self.file_helper(file, reverse)
                    std_dict["stdout"] = stdout
                except FileNotFoundError:
                    errMessage = f"Sort: {file}: No such file or directory"
                    std_dict["stderr"] = errMessage
                    std_dict["exit_code"] = "1"
                return std_dict

        lines = []
        input = list(stdin)
        [lines.extend(i.splitlines()) for i in input]
        stdout = self.helper(lines, reverse)
        std_dict["stdout"] = stdout
        return std_dict

    @classmethod
    def file_helper(cls, file, reverse):
        with open(file, "r") as f:
            lines = f.read().splitlines()
            output = cls.helper(lines, reverse)
        return output

    @classmethod
    def helper(cls, lines, reverse):
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
    """
    Recursively searches for files with matching names.
    Outputs the list of relative paths, each followed by a newline.
    """

    def exec(self, args, stdin=None):
        """
        :param args: Arguments
        :param stdin: Standard input
        :returns: A dictionary of Standard output, Standard Error and exit_code
        """
        std_dict = {"stdout": deque(), "stderr": deque(), "exit_code": 0}
        stdout = deque()
        if len(args) > 3:
            std_dict["stderr"] = "Find: Wrong number of command line arguments"
            std_dict["exit_code"] = "1"
            return std_dict
        if len(args) == 3:
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

    @classmethod
    def helper(cls, pattern, stack, res):
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


class LocalApp:
    '''
    Make applications in the same directory, same environment path, or otherwise provided app become callable
    '''

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

    @classmethod
    def _get_system_executables(cls, app, path):
        possibleExecutable = [app]
        if sys.platform == "win32":
            if os.curdir not in path:
                # add current directory to path so
                # applications are found in current dir
                path.append(os.curdir)

            pathExtensions = os.getenv("PATHEXT").split(os.pathsep)
            pathExtensionList = [e for e in pathExtensions if e is not None]

            possibleExecutable = self._get_possible_exec(app, pathExtensionList)
        return possibleExecutable

    @classmethod
    def _get_possible_exec(cls, app, pathExtensionList):
        for extension in pathExtensionList:
            if app.lower().endswith(extension.lower()):
                possibleExecutable = [app]
                break
        else:
            possibleExecutable = [app + extension for extension in pathExtensionList]

        return possibleExecutable

    @classmethod
    def _is_valid_path_to_executable(
            cls, executablePath, existsAndExecutable=os.F_OK | os.X_OK
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
            if error == "":
                stdout.append(output)
            else:
                raise Exception(f"{self.app}: " + error)
        else:
            std_dict["stderr"] = f"No application {self.app} is found\n"
        std_dict["stdout"] = stdout
        return std_dict
