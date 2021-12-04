from apps import Pwd, Cd, Echo, Ls, Cat, Head, Tail, Grep, NotSupported


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

        app = self.menu.get(appName, NotSupported(appName))
        return app
