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
        return visitor.visit_single_quote(self)


class DoubleQuote(AST):
    def __init__(self, quotedPart, containSubstitution):
        self.containSubstitution = containSubstitution
        self.quotedPart = quotedPart
        assert isinstance(self.quotedPart, Iterable)

    def accept(self, visitor):
        return visitor.visit_double_quote(self)


class Substitution(AST):
    def __init__(self, quoted):
        self.quoted = "{}".format(quoted)
        assert isinstance(self.quoted, str)

    def accept(self, visitor):
        res = visitor.visit_sub(self)
        return res


class RedirectIn(AST):
    def __init__(self, arg) -> None:
        self.arg = arg

    def accept(self, visitor):
        return visitor.visit_redirect_in(self)


class RedirectOut(AST):
    def __init__(self, arg) -> None:
        self.arg = arg

    def accept(self, visitor, stdin=None):
        return visitor.visit_redirect_out(self, stdin)


class Call(AST):
    def __init__(self, redirects, appName, args) -> None:
        self.redirects = redirects
        self.appName = appName
        self.args = args
        assert isinstance(args, Iterable)
        assert all(isinstance(arg, Iterable) for arg in args)
        assert len(redirects) <= 2

    def accept(self, visitor, input=None):
        return visitor.visit_call(self, in_put=input)


class Seq(AST):
    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right
        assert left is not None and right is not None

    def accept(self, visitor):
        return visitor.visit_seq(self)


class Pipe(AST):
    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right
        assert left is not None and right is not None

    def accept(self, visitor):
        return visitor.visit_pipe(self)
