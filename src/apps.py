import re
import sys
import os
from os import listdir
from collections import deque
from abc import ABC, abstractmethod
import fnmatch


class Application(ABC):
    @classmethod
    def exec(self, args, stdin):
        raise (Exception(NotImplementedError))


class Pwd(Application):
    def exec(self, args, stdin=None):
        stdout = deque()
        stdout.append(os.getcwd())
        return stdout


class Cd(Application):
    def exec(self, args, stdin=None):
        if len(args) == 0 or len(args) > 1:
            raise ValueError("wrong number of command line arguments")
        os.chdir(args[0])
        # print("apps/Cd: " + os.getcwd())


class Echo(Application):
    def exec(self, args, stdin=None):
        stdout = deque()
        # print(args)
        stdout.append(" ".join(args) + "\n")
        return stdout


class Ls:
    def exec(self, args, stdin=None):
        stdout = deque()
        if len(args) == 0:
            ls_dir = os.getcwd()
        elif len(args) > 1:
            raise ValueError("wrong number of command line arguments")
        else:
            ls_dir = args[0]
        for f in listdir(ls_dir):
            if not f.startswith("."):
                stdout.append(f + "\n")
        return stdout


class Cat:
    def exec(self, args, stdin=None):
        stdout = deque()

        if stdin:
            with open(stdin) as f:
                stdout.append(f.read())
        else:
            for a in args:
                with open(a) as f:
                    stdout.append(f.read())

        return stdout


class Head:
    def exec(self, args, stdin=None):
        stdout = deque()
        # print(stdin)
        if stdin:
            if len(args) != 0 and len(args) != 2:
                raise ValueError("wrong number of command line arguments")
            if len(args) == 0:
                num_lines = 10
            if len(args) == 2:
                if args[0] != "-n":
                    raise ValueError("wrong flags")
                else:
                    num_lines = int(args[1])
            with open(stdin) as f:
                lines = f.readlines()
                for i in range(0, min(len(lines), num_lines)):
                    stdout.append(lines[i])
        else:
            if len(args) != 1 and len(args) != 3:
                raise ValueError("wrong number of command line arguments")
            if len(args) == 1:
                num_lines = 10
                file = args[0]
            if len(args) == 3:
                if args[0] != "-n":
                    raise ValueError("wrong flags")
                else:
                    num_lines = int(args[1])
                    file = args[2]
            with open(file) as f:
                lines = f.readlines()
                for i in range(0, min(len(lines), num_lines)):
                    stdout.append(lines[i])
        return stdout


class Tail:
    def exec(self, args, stdin=None):
        stdout = deque()
        # print(stdin)
        if stdin:
            if len(args) != 0 and len(args) != 2:
                raise ValueError("wrong number of command line arguments")
            if len(args) == 0:
                num_lines = 10
            if len(args) == 2:
                if args[0] != "-n":
                    raise ValueError("wrong flags")
                else:
                    num_lines = int(args[1])
            with open(stdin) as f:
                lines = f.readlines()
                display_length = min(len(lines), num_lines)
                for i in range(0, min(len(lines), num_lines)):
                    stdout.append(lines[len(lines) - display_length + i])
        else:
            if len(args) != 1 and len(args) != 3:
                raise ValueError("wrong number of command line arguments")
            if len(args) == 1:
                num_lines = 10
                file = args[0]
            if len(args) == 3:
                if args[0] != "-n":
                    raise ValueError("wrong flags")
                else:
                    num_lines = int(args[1])
                    file = args[2]
            with open(file) as f:
                lines = f.readlines()
                display_length = min(len(lines), num_lines)
                for i in range(0, display_length):
                    stdout.append(lines[len(lines) - display_length + i])
        return stdout


class Grep:
    def exec(self, args, stdin=None):
        # print("args: ", args)
        stdout = deque()
        if len(args) < 2:
            raise ValueError("wrong number of command line arguments")
        pattern = args[0]
        # print(pattern)
        files = args[1:]
        for file in files:
            with open(file) as f:
                lines = f.readlines()

                for line in lines:
                    if re.match(pattern, line):

                        if len(files) > 1:
                            stdout.append(f"{file}:{line}")
                        else:
                            # print(line)
                            stdout.append(line)
        return stdout


class Cut:
    def exec(self, args, stdin=None):
        stdout = deque()
        if len(args) > 3:
            raise ValueError("wrong number of command line arguments")
        elif len(args) == 3:
            if args[0] != "-b":
                raise ValueError("wrong flags")
            pattern = args[1]
            file = args[2]
        else:
            if args[0] != "-b":
                raise ValueError("wrong flags")
            pattern = args[1]
            cmdline = input()
            file = cmdline
        with open(file) as f:
            pattern_list = pattern.split(",")

            # 但有一点要注意，cut命令如果使用了-b选项，那么执行此命令时，cut会先把-b后面所有的定位进行从小到大排序，然后再提取。
            # stdout.
            lines = f.readlines()

            for line in lines:
                for p in pattern_list:
                    if "-" in p:
                        start_i, end_i = p.split("-")
                        # if start_i == None:
                        #     start_i = 0
                        # if end_i == None:
                        #     end_i == len(line)
                        print("开始", start_i)
                        start_i, end_i = int(start_i), int(end_i)
                        print(start_i, end_i)
                        print(line[start_i:end_i])
                        stdout.append(line[start_i:end_i])
                    else:
                        stdout.append(line)
            print(pattern_list)

        return stdout


class Find:
    def exec(self, args, stdin=None):
        stdout = deque()
        if len(args) > 3:
            raise ValueError("wrong number of command line arguments")
        elif len(args) == 3:
            if args[1] != "-name":
                raise ValueError("wrong flags")
            pattern = args[2]
            dict = args[0]
        else:
            if args[0] != "-name":
                raise ValueError("wrong flags")
            pattern = args[1]
            dict = os.getcwd()
        for path, dirlist, filelist in os.walk(dict):
            for name in fnmatch.filter(filelist, pattern):
                stdout.append(name)
        return stdout


class NotSupported:
    def __init__(self, app_token):
        self.app_token = app_token

    def exec(self, out, args):
        raise ValueError(f"unsupported application {self.app_token}")


from collections import deque

if __name__ == "__main__":
    # print("Pwd",Pwd().exec())
    # print("Ls",Ls().exec(args=[]))
    # print("Ls", Ls().exec(args=["F:\\OneDrive\\OneDrive - University College London\\"]))
    print("Cat", Cat().exec(args=["*.py"]))
    print("Grep", Grep().exec(args=["test file 3*", "test.txt"]))
    print("Head", Head().exec(args=["-n", 3, "test.txt"]))
    print("Tail", Tail().exec(args=["-n", 3, "test.txt"]))
    print("Echo", Echo().exec(args=["test"]))
    print("Find local", Find().exec(args=["-name", "parsercombinator.*"]))
    print("Find local", Find().exec(args=[".\doc", "-name", "*.py"]))
    # print("Cut file", Cut().exec(args=["-b", '5-7,1-8', 'test.txt']))
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
