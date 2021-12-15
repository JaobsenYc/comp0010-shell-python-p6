from apps import *


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()

        return _instance[cls]

    return inner


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

    def getApp(self, appName, *remain):
        # appName = appName[0].upper() + appName[1:]
        # if appName not in self.menu:
        #     cls = type(
        #         appName, (), {}
        #     )
        #     self.menu[appName] = cls
        # else:
        #     cls = self.menu[appName]

        app = self.menu.get(appName, LocalApp(appName))
        return app
