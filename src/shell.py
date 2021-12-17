import re
import sys
import os
from os import listdir
from collections import deque
from glob import glob
from apps import *
from parsercombinator import command
from visitor import ASTVisitor
import traceback

# def eval()

if __name__ == "__main__":
    visitor = ASTVisitor()
    out = deque()
    args_num = len(sys.argv) - 1
    if args_num > 0:
        if args_num != 2:
            raise ValueError("wrong number of command line arguments")
        if sys.argv[1] != "-c":
            raise ValueError(f"unexpected command line argument {sys.argv[1]}")
        cmd = command.parse(sys.argv[2])
        # print(seq)
        try:
            out = cmd.accept(visitor)
            if out["exit_code"]:
                print("".join(out["stdout"]), end="")
                print("".join(out["stderr"]), end="")
            else:
                print("".join(out["stdout"]), end="")
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)

        # while len(out) > 0:
        #     line = out.popleft()
        #     print(line, end="")
        # print("".join(out["stdout"]), end="")
    else:
        while True:
            print(os.getcwd() + "> ", end="")
            cmdline = input()
            # print(cmdline)
            cmd = command.parse(cmdline)
            # out = cmd.accept(visitor)

            # while len(out) > 0:
            #     line = out.popleft()
            #     print(line, end="")
            try:
                out = cmd.accept(visitor)
                if out["exit_code"]:
                    print("".join(out["stdout"]), end="")
                    print("".join(out["stderr"]), end="")
                else:
                    print("".join(out["stdout"]), end="")
            except Exception:
                print(traceback.format_exc(), file=sys.stderr)
