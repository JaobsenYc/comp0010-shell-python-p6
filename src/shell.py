import sys
import os
from parsercombinator import command
from visitor import ASTVisitor
import traceback
from parsy import ParseError


def eval(cmdline):
    visitor = ASTVisitor()
    try:
        cmd = command.parse(cmdline)
    except ParseError:
        print(traceback.format_exc(), file=sys.stderr)
        return

    try:
        out = cmd.accept(visitor)
        if out["exit_code"]:
            print("".join(out["stdout"]), end="")
            print("".join(out["stderr"]), end="")
        else:
            print("".join(out["stdout"]), end="")
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)


def handle_arg_case(args=[]):
    args_num = len(args) - 1
    if args_num > 0:
        if args_num != 2:
            raise ValueError("wrong number of command line arguments")
        if args[1] != "-c":
            raise ValueError(f"unexpected command line argument {args[1]}")
        eval(args[2])
    else:
        while True:
            print(os.getcwd() + "> ", end="")
            eval(input())


if __name__ == "__main__":
    handle_arg_case(sys.argv)
