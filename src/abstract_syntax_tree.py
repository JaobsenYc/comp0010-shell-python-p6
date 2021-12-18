from abc import ABC, abstractmethod
from collections.abc import Iterable


class AST(ABC):
    @abstractmethod
    def accept(self, visitor):
        """Abstract accept method"""


class SingleQuote(AST):
    def __init__(self, quotedPart):
        assert type(quotedPart) == str
        self.quotedPart = quotedPart

    def accept(self, visitor):
        return visitor.visitSingleQuote(self)

    def __str__(self):
        return "SingleQ({})".format(str(self.quotedPart))

    def __repr__(self):
        return "SingleQ({})".format(str(self.quotedPart))


class DoubleQuote(AST):
    def __init__(self, quotedPart, containSubstitution):
        self.containSubstitution = containSubstitution
        self.quotedPart = quotedPart
        assert isinstance(self.quotedPart, Iterable)

    def accept(self, visitor):
        return visitor.visitDoubleQuote(self)

    def __str__(self):
        return "DoubleQ({})".format(str(self.quotedPart))

    def __repr__(self):
        return "DoubleQ({})".format(str(self.quotedPart))


class Substitution(AST):
    def __init__(self, quoted):
        self.quoted = "{}".format(quoted)
        assert isinstance(self.quoted, str)

    def accept(self, visitor):
        res = visitor.visitSub(self)
        return res

    def __str__(self) -> str:
        return f"Subeval({str(self.quoted)})"

    def __repr__(self) -> str:
        return f"Subeval({str(self.quoted)})"


class RedirectIn(AST):
    def __init__(self, arg) -> None:
        self.arg = arg
        assert len(arg) >= 1

    def accept(self, visitor):
        return visitor.visitRedirectIn(self)

    def __str__(self) -> str:
        return f"RediectIn({str(self.arg)})"

    def __repr__(self) -> str:
        return f"RediectIn({str(self.arg)})"


class RedirectOut(AST):
    def __init__(self, arg) -> None:
        self.arg = arg
        assert len(arg) == 1

    def accept(self, visitor, stdin=None):
        return visitor.visitRedirectOut(self, stdin)

    def __str__(self) -> str:
        return f"RediectOut({str(self.arg)})"

    def __repr__(self) -> str:
        return f"RediectOut({str(self.arg)})"


class Call(AST):
    def __init__(self, redirects, appName, args) -> None:
        self.redirects = redirects
        self.appName = appName
        self.args = args
        assert isinstance(args, Iterable)
        assert all(isinstance(arg, Iterable) for arg in args)
        assert len(redirects) < 2

    def accept(self, visitor, input=None):
        return visitor.visitCall(self, input=input)

    def __str__(self) -> str:
        return f"Call(\
                {str(self.redirects)}, \
                {str(self.appName)}, \
                {str(self.args)})"


class Seq(AST):
    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right
        assert left is not None and right is not None

    def accept(self, visitor):
        return visitor.visitSeq(self)

    def __str__(self) -> str:
        return f"Seq({str(self.left)}, {str(self.right)})"


class Pipe(AST):
    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right
        assert left is not None and right is not None

    def accept(self, visitor):
        return visitor.visitPipe(self)

    def __str__(self) -> str:
        return f"Pipe({str(self.left)}, {str(self.right)})"
