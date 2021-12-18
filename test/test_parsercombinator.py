import unittest
from collections import deque

import parsercombinator as pc
from hypothesis import given
from hypothesis import strategies as st
from hypothesis_regex import regex


class TestParserCombinator(unittest.TestCase):
    def test_constants(self):
        assert pc.pipeOp.parse("|") == "|"
        assert pc.semiOp.parse(";") == ";"
        assert pc.lessThan.parse("<") == "<"
        assert pc.greaterThan.parse(">") == ">"

    @given(regex(" *"))
    def test_whitespace(self, spaces):
        assert pc.greaterThan.parse(spaces) == spaces


if __name__ == "__main__":
    unittest.main()
