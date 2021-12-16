import re
import sys
import os
from os import listdir
from collections import deque
from glob import glob
from apps import *
from parsercombinator import command
from visitor import ASTVisitor

if __name__ == "__main__":
    visitor = ASTVisitor()
    out=""
    args_num = len(sys.argv) - 1
    if args_num > 0:
        if args_num != 2:
            raise ValueError("wrong number of command line arguments")
        if sys.argv[1] != "-c":
            raise ValueError(f"unexpected command line argument {sys.argv[1]}")
        seq = command.parse(sys.argv[2])
        out = seq.accept(visitor)
        print("out: ", len(out))

        while len(out) > 0:
            print(True)
            line = out.popleft()
            print(line, end="")

    else:
        while True:
            print(os.getcwd() + "> ", end="")
            cmdline = input()
            seq = command.parse(cmdline)
            out = seq.accept(visitor)

            while len(out) > 0:
                print(True)
                line = out.popleft()
                print("len: ", len(out))
                print(line, end="")
