import sys
import os
from collections import deque
from src.parsercombinator import command
from src.visitor import ASTVisitor
import traceback

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

        try:
            out = cmd.accept(visitor)
            if out["exit_code"]:
                print("".join(out["stdout"]), end="")
                print("".join(out["stderr"]), end="")
            else:
                print("".join(out["stdout"]), end="")
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)

    else:
        while True:
            print(os.getcwd() + "> ", end="")
            cmdline = input()
            cmd = command.parse(cmdline)

            try:
                out = cmd.accept(visitor)
                if out["exit_code"]:
                    print("".join(out["stdout"]), end="")
                    print("".join(out["stderr"]), end="")
                else:
                    print("".join(out["stdout"]), end="")
            except Exception:
                print(traceback.format_exc(), file=sys.stderr)
