from apps import (
    Pwd,
    Cd,
    Echo,
    Ls,
    Cat,
    Head,
    Tail,
    Grep,
    Cut,
    Find,
    Sort,
    Uniq,
    LocalApp,
)
import re


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()

        return _instance[cls]

    return inner


# class ShellException(Exception):


@singleton
class AppDecorator:
    def decorateSafe(self, cls):
        originalExec = cls.exec

        def newExec(args, stdin=None):

            executedProcess = originalExec(args, stdin=stdin)
            if executedProcess["exit_code"]:
                raise Exception("".join(executedProcess["stderr"]))
            else:
                return executedProcess

        cls.exec = newExec
        return cls

    def decorateUnsafe(self, cls):
        # def newExec(args, stdin=None):

        #     try:
        #         executedProcess = cls.exec(args, stdin=stdin)
        #         if executedProcess["exit_code"]:
        #             raise Exception(args, "".join(executedProcess["stderr"]))
        #         return executedProcess
        #     except Exception as e:
        #         print("{}: {}".format(e.args[0], e.args[1]))

        # cls.newExec = newExec
        return cls


@singleton
class AppsFactory:
    def __init__(self):
        self.menu = {
            "pwd": Pwd(),
            "cd": Cd(),
            "echo": Echo(),
            "ls": Ls(),
            "cat": Cat(),
            "head": Head(),
            "tail": Tail(),
            "grep": Grep(),
            "cut": Cut(),
            "find": Find(),
            "sort": Sort(),
            "uniq": Uniq(),
        }

        self.appType = {
            "^_": lambda name, menu, default: AppDecorator().decorateUnsafe(
                menu.get(name[1:], default(name[1:]))
            ),
            ".*": lambda name, menu, default: AppDecorator().decorateSafe(
                menu.get(name, default(name))
            ),
        }

    def getApp(self, appName, *remain):
        for regex, decorator in self.appType.items():
            if re.search(regex, appName):
                return decorator(appName, self.menu, LocalApp)
