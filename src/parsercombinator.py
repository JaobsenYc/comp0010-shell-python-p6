from parsy import regex, string, generate, seq
from glob import glob
from apps import *
from operators import *


space = regex("\s+")
optional_space = space.optional()
semi = string(";")
word = regex("[^\"'\\s;]+").desc("executable command or argument")
openParen = string("(")
closeParen = string(")")


@generate
def string_():
    s = yield regex("\"[^\"]+\"|'[^']+'").desc("quoted characters")
    return s[1:-1]


@generate
def globbed_word():
    w = yield regex("[^\"'\\s;]+").desc("executable command or argument")
    return glob(w) or w


@generate
def arguments():
    flat_args = []
    args = yield (space >> (string_ | globbed_word)).many()
    for item in args:
        if isinstance(item, list):
            flat_args.extend(item)
        else:
            flat_args.append(item)
    return flat_args


# arguments = (space >> (string_ | word)).many()

expression = seq(word, arguments)


@generate
def complex_expression():
    e = yield expression
    root = Expression(e)
    while True:
        yield optional_space
        s = yield semi.optional()
        if s:
            yield optional_space
            next_expression = yield expression
            operator = SemiColon(root, Expression(next_expression))
            root = operator
        else:
            break
    return root


print(complex_expression.parse("echo hi; echo danny"))
