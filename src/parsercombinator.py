from parsy import generate, regex, seq, string

from src import abstract_syntax_tree

pipeOp = string("|")
semiOp = string(";")
nonKeyWord = regex("[^`\"'\\s;|\n]+").desc("not keyword string")


@generate
def singleQuoted():
    content = yield regex("'[^'\n]*'")
    return abstract_syntax_tree.SingleQuote(content[1:-1])


@generate
def backQuoted():
    content = yield regex("`[^`\n]*`")
    return abstract_syntax_tree.Substitution(content[1:-1])


@generate
def doubleQuoted():
    yield string('"')
    middle = yield (backQuoted | regex('[^\n`"]')).many()
    yield string('"')

    # This shows if there is any substitutble parts in this quote
    hasSub = False
    for n, i in enumerate(middle):
        if isinstance(i, abstract_syntax_tree.Substitution):
            hasSub = True
            break

    return abstract_syntax_tree.DoubleQuote(middle, hasSub)


@generate
def quoted():
    text = yield singleQuoted | backQuoted | doubleQuoted
    return text


whitespace = regex("\\s*")
lessThan = string("<")
greaterThan = string(">")


@generate
def unquoted():
    s = yield regex("[^\\s\\t'\"`\n;|<>]+")
    return s


argument = (quoted | unquoted).at_least(1)


@generate
def redirection():
    sign = yield lessThan | greaterThan
    arg = yield whitespace >> unquoted
    if sign == "<":
        return abstract_syntax_tree.RedirectIn(arg)
    else:
        return abstract_syntax_tree.RedirectOut(arg)


atom = redirection | argument


@generate
def call():
    redirections = yield whitespace >> (redirection << whitespace).many()
    callName = yield backQuoted | unquoted | doubleQuoted
    mixed_args = yield (whitespace >> atom).many() << whitespace
    args = []
    # separate the redirects with quoted args
    for a in mixed_args:
        if (
            type(a) is abstract_syntax_tree.RedirectOut
            or type(a) is abstract_syntax_tree.RedirectIn
        ):
            redirections.append(a)
        else:
            args.append(a)
    return abstract_syntax_tree.Call(redirections, callName, args)


sequ = seq(semiOp, call)
pipe = seq(pipeOp, call)


@generate
def command():
    basis = yield call
    additional = yield (pipe | sequ).many()
    # construct a recursive tree
    for addition in additional:
        if addition[0] == ";":
            basis = abstract_syntax_tree.Seq(basis, addition[1])
        else:
            basis = abstract_syntax_tree.Pipe(basis, addition[1])
    return basis
