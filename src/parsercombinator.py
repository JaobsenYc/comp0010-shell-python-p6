from parsy import regex, string, generate, seq
from glob import glob
from apps import *
import abstract_syntax_tree
from operators import *

pipeOp = string("|")
semiOp = string(";")
nonKeyWord = regex("[^`\"'\\s;|\n]+").desc("not keyword string")


@generate
def singleQuoted():
    content = yield regex("'[^'\n]*'")
    return content


@generate
def backQuoted():
    content = yield regex("`[^`\n]*`")
    return abstract_syntax_tree.Substitution(content[1:-1])


@generate
def doubleQuoted():
    yield string('"')
    middle = yield (backQuoted | regex('[^\n`"]')).many()
    yield string('"')
    return f'"{"".join(middle)}"'


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
    return glob(s) or [s]


argument = quoted | unquoted  # .at_least(1)
# redirection = seq(lessThan | greaterThan, whitespace >> argument)
@generate
def redirection():
    sign = yield lessThan | greaterThan
    arg = yield whitespace >> unquoted
    if sign == "<":
        return abstract_syntax_tree.RedirectIn(arg)
    else:
        return abstract_syntax_tree.RedirectOut(arg)


atom = redirection | argument
# call = seq(
#     whitespace >> (redirection << whitespace).many(),
#     argument,
#     (whitespace >> atom).many() << whitespace,
# )
@generate
def call():
    redirections = yield whitespace >> (redirection << whitespace).many()
    callName = yield backQuoted | unquoted
    mixed_args = yield (whitespace >> atom).many() << whitespace
    args = []
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
# command = seq(call, (pipe | sequ).many())
@generate
def command():
    basis = yield call
    additional = yield (pipe | sequ).many()
    for addition in additional:
        if addition[0] == ";":
            basis = abstract_syntax_tree.Seq(basis, addition[1])
        else:
            basis = abstract_syntax_tree.Pipe(basis, addition[1])
    return basis


if __name__ == "__main__":
    # print(command.parse("< *.py call a b \"a\" > out| hello `echo arg` *.py *s.py ; cat a "))
    print(command.parse('< *.py call a b "a" > out'))

# space = regex("\s+")
# optional_space = space.optional()
# semi = string(";")
# word = regex("[^\"'\\s;]+").desc("executable command or argument")
# openParen = string("(")
# closeParen = string(")")


# @generate
# def string_():
#     s = yield regex("\"[^\"]+\"|'[^']+'").desc("quoted characters")
#     return s[1:-1]


# @generate
# def globbed_word():
#     w = yield regex("[^\"'\\s;]+").desc("executable command or argument")
#     return glob(w) or w


# @generate
# def arguments():
#     flat_args = []
#     args = yield (space >> (string_ | globbed_word)).many()
#     for item in args:
#         if isinstance(item, list):
#             flat_args.extend(item)
#         else:
#             flat_args.append(item)
#     return flat_args


# # arguments = (space >> (string_ | word)).many()

# expression = seq(word, arguments)


# @generate
# def complex_expression():
#     e = yield expression
#     root = Expression(e)
#     while True:
#         yield optional_space
#         s = yield semi.optional()
#         if s:
#             yield optional_space
#             next_expression = yield expression
#             operator = SemiColon(root, Expression(next_expression))
#             root = operator
#         else:
#             break
#     return root


# if __name__ == "__main__":
#     print(complex_expression.parse("echo hi; echo danny"))
