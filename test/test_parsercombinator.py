import unittest

from src import parsercombinator as pc
from src.abstract_syntax_tree import (
    DoubleQuote,
    Substitution,
    SingleQuote,
    DoubleQuote,
    RedirectIn,
    RedirectOut,
    Call,
    Pipe,
    Seq,
)
from hypothesis import given
from hypothesis import strategies as st


class TestParserCombinator(unittest.TestCase):
    def test_constants(self):
        assert pc.pipeOp.parse("|") == "|"
        assert pc.semiOp.parse(";") == ";"
        assert pc.lessThan.parse("<") == "<"
        assert pc.greaterThan.parse(">") == ">"

    @given(space=st.from_regex(r"^ *$"))
    def test_whitespace(self, space):
        space = space.strip("\n")
        assert pc.whitespace.parse(space) == space

    @given(word=st.from_regex(r"^[^`\"'\s;|\n]+$"))
    def test_nonKeyWord(self, word):
        word = word.strip("\n")
        assert pc.nonKeyWord.parse(word) == word

    @given(word=st.from_regex(r"^'[^'\n]*'$"))
    def test_singleQuote(self, word):
        word = word.strip("\n")
        sq = pc.singleQuoted.parse(word)
        assert sq.quotedPart == word[1:-1]

    @given(word=st.from_regex(r"^`[^`\n]*`$"))
    def test_backQuote(self, word):
        word = word.strip("\n")
        bq = pc.backQuoted.parse(word)
        assert bq.quoted == word[1:-1]

    def test_doubleQuote(self):
        word = "\"`echo cat` hello.txt 'abc'\""
        dq = pc.doubleQuoted.parse(word)
        assert isinstance(dq.quotedPart[0], Substitution)
        assert dq.quotedPart[0].quoted == "echo cat"
        assert "".join(dq.quotedPart[1:]) == " hello.txt 'abc'"

        word = '"Full String"'
        dq = pc.doubleQuoted.parse(word)
        assert "".join(dq.quotedPart) == "Full String"

    def test_quoted(self):
        word = '"aabbcc`asd`"'
        q = pc.quoted.parse(word)
        assert isinstance(q, DoubleQuote)
        word = "'aabbcc'"
        q = pc.quoted.parse(word)
        assert isinstance(q, SingleQuote)
        word = "`aabbcc`"
        q = pc.quoted.parse(word)
        assert isinstance(q, Substitution)

    @given(word=st.from_regex(r"^[^\s\t'\"`\n;|<>]+$"))
    def test_unquoted(self, word):
        word = word.strip("\n")
        uq = pc.unquoted.parse(word)
        assert uq == word

    def test_argument(self):
        word = "`echo cat`hello.txt'abc'\"`echo hey`wow\""
        arg = pc.argument.parse(word)
        types = [Substitution, str, SingleQuote, DoubleQuote]
        for i in range(4):
            assert isinstance(arg[i], types[i])

    @given(word=st.from_regex(r"^(<|>)( *)[^\s\t'\"`\n;|<>]+$"))
    def test_redirect(self, word):
        word = word.strip("\n")
        redirect = pc.redirection.parse(word)
        assert isinstance(redirect, RedirectOut) or isinstance(redirect, RedirectIn)

    def test_atom(self):
        word = "< text.txt"
        atom = pc.atom.parse(word)
        possibleTypes = [
            RedirectOut,
            RedirectIn,
            str,
            SingleQuote,
            DoubleQuote,
            Substitution,
        ]
        assert any([isinstance(atom, x) for x in possibleTypes])

    def test_call(self):
        word = "< text.txt call `hello.txt` > output.txt"
        call = pc.call.parse(word)
        assert len(call.redirects) == 2
        assert call.appName == "call"
        assert len(call.args) == 1 and isinstance(call.args[0][0], Substitution)

    def test_seq(self):
        word = "; < text.txt call `hello.txt` > output.txt"
        sequ = pc.sequ.parse(word)
        assert sequ[0] == ";" and isinstance(sequ[1], Call)

    def test_pipe(self):
        word = "| < text.txt call `hello.txt` > output.txt"
        pipe = pc.pipe.parse(word)
        assert pipe[0] == "|" and isinstance(pipe[1], Call)

    def test_command(self):
        word = "< *.py hello | < text.txt call `hello.txt` > output.txt ; ls"
        cmd = pc.command.parse(word)
        assert self._helper_commandTesting(cmd)

    def _helper_commandTesting(self, command):
        if isinstance(command, Pipe) or isinstance(command, Seq):
            return self._helper_commandTesting(
                command.left
            ) and self._helper_commandTesting(command.right)
        elif isinstance(command, Call):
            return True
        else:
            return False


if __name__ == "__main__":
    unittest.main()
