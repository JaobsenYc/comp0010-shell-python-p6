from parsy import regex, string, generate, seq
from glob import glob
from apps import *
from operators import *

pipeOp = string("|")
semiOp = string(";")
nonKeyWord = regex("[^`\"'\\s;|\n]+").desc("not keyword string")

singleQuoted = regex("'[^'\n]*'")
backQuoted = regex("`[^`\n]*`")


@generate
def doubleQuoted():
    start = yield string('"')
    middle = yield (backQuoted | regex('[^\n`"]')).many()
    last = yield string('"')
    return start + "".join(middle) + last


@generate
def quoted():
    text = yield singleQuoted | backQuoted | doubleQuoted
    return text[1:-1]


whitespace = regex("\\s*")
lessThan = string("<")
greaterThan = string(">")
unquoted = regex("[^\\s\\t'\"`\n;|<>]+")
argument = quoted | unquoted  # .at_least(1)
redirection = seq(lessThan | greaterThan, whitespace >> argument)
atom = redirection | argument
call = seq(
    whitespace >> (redirection << whitespace).many(),
    argument,
    (whitespace >> atom).many() << whitespace,
)


sequ = seq(semiOp, call)
pipe = seq(pipeOp, call)
command = seq(call, (pipe | sequ).many())


if __name__ == "__main__":
    print(command.parse("< hello.txt > narnia.csv hello -t 'yes'| cat | scru output"))

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
