import re
import sys
import os
from os import listdir
from collections import deque
from glob import glob
from apps import *

def parse_commands(cmdline):
    raw_commands = []
    for m in re.finditer("([^\"';]+|\"[^\"]*\"|'[^']*')", cmdline):
        if m.group(0):
            raw_commands.append(m.group(0))
    return raw_commands


def get_tokens(command):
    tokens = []
    for m in re.finditer("[^\\s\"']+|\"([^\"]*)\"|'([^']*)'", command):
        if m.group(1) or m.group(2):
            quoted = m.group(0)
            tokens.append(quoted[1:-1])
        else:
            globbing = glob(m.group(0))
            if globbing:
                tokens.extend(globbing)
            else:
                tokens.append(m.group(0))
    return tokens[0], tokens[1:]
            

def eval(cmdline, out):
    raw_commands = parse_commands(cmdline)
    for command in raw_commands:
        app_token, args = get_tokens(command)
        app = {
            "pwd": Pwd(),
            "cd": Cd(),
            "echo": Echo(),
            "ls": Ls(),
            "cat": Cat(),
            "head": Head(),
            "tail": Tail(),
            "grep": Grep()
        }.get(app_token, NotSupported(app_token))
        app.exec(out, args)




if __name__ == "__main__":
    args_num = len(sys.argv) - 1
    if args_num > 0:
        if args_num != 2:
            raise ValueError("wrong number of command line arguments")
        if sys.argv[1] != "-c":
            raise ValueError(f"unexpected command line argument {sys.argv[1]}")
        out = deque()
        eval(sys.argv[2], out)
        while len(out) > 0:
            print(out.popleft(), end="")
    else:
        while True:
            print(os.getcwd() + "> ", end="")
            cmdline = input()
            out = deque()
            eval(cmdline, out)
            while len(out) > 0:
                print(out.popleft(), end="")
