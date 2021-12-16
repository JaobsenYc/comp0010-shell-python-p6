jaobsenyc@JaobsenYc:/mnt/f/OneDrive/OneDrive - University College London/UCL/COMP0010/comp0010-shell-python-p6$ python3 system_test/tests.py -v
[+] Building 0.2s (6/6) FINISHED
 => [internal] load build definition from Dockerfile                                                                                                                                                                                                                                                               0.0s
 => => transferring dockerfile: 82B                                                                                                                                                                                                                                                                                0.0s
 => [internal] load .dockerignore                                                                                                                                                                                                                                                                                  0.0s
 => => transferring context: 2B                                                                                                                                                                                                                                                                                    0.0s
 => [internal] load metadata for docker.io/library/comp0010-system-test:latest                                                                                                                                                                                                                                     0.0s
 => [1/2] FROM docker.io/library/comp0010-system-test                                                                                                                                                                                                                                                              0.0s
 => CACHED [2/2] WORKDIR /test                                                                                                                                                                                                                                                                                     0.0s
 => exporting to image                                                                                                                                                                                                                                                                                             0.1s
 => => exporting layers                                                                                                                                                                                                                                                                                            0.0s
 => => writing image sha256:150d3a89e1735c4b9b7f07460d735e33ecdc27c6424335fd7cc96b8dc279a920                                                                                                                                                                                                                       0.0s
 => => naming to docker.io/library/comp0010-test-image                                                                                                                                                                                                                                                             0.0s

Use 'docker scan' to run Snyk tests against images to find vulnerabilities and learn how to fix them
test_cat (__main__.TestFEL) ... ok
test_cat_stdin (__main__.TestFEL) ... ok
test_cd_pwd (__main__.TestFEL) ... ok
test_cut (__main__.TestFEL) ... ok
test_cut_interval (__main__.TestFEL) ... ok
test_cut_open_interval (__main__.TestFEL) ... ok
test_cut_overlapping (__main__.TestFEL) ... ok
test_cut_stdin (__main__.TestFEL) ... ok
test_cut_union (__main__.TestFEL) ... ok
test_disabled_doublequotes (__main__.TestFEL) ... ok
test_doublequotes (__main__.TestFEL) ... ok
test_echo (__main__.TestFEL) ... ok
test_find (__main__.TestFEL) ... ok
test_find_dir (__main__.TestFEL) ... ok
test_find_pattern (__main__.TestFEL) ... ok
test_globbing (__main__.TestFEL) ... ok
test_globbing_dir (__main__.TestFEL) ... ok
test_grep (__main__.TestFEL) ... ok
test_grep_files (__main__.TestFEL) ... ok
test_grep_no_matches (__main__.TestFEL) ... ok
test_grep_re (__main__.TestFEL) ... ok
test_grep_stdin (__main__.TestFEL) ... ok
test_head (__main__.TestFEL) ... ok
test_head_n0 (__main__.TestFEL) ... ok
test_head_n5 (__main__.TestFEL) ... ok
test_head_n50 (__main__.TestFEL) ... ok
test_head_stdin (__main__.TestFEL) ... ok
test_input_redirection (__main__.TestFEL) ... ok
test_input_redirection_infront (__main__.TestFEL) ... ok
test_input_redirection_nospace (__main__.TestFEL) ... ok
test_ls (__main__.TestFEL) ... ok
test_ls_dir (__main__.TestFEL) ... ok
test_ls_hidden (__main__.TestFEL) ... ok
test_nested_doublequotes (__main__.TestFEL) ... ok
test_output_redirection (__main__.TestFEL) ... FAIL
test_output_redirection_overwrite (__main__.TestFEL) ... FAIL
test_pipe_chain_sort_uniq (__main__.TestFEL) ... FAIL
test_pipe_uniq (__main__.TestFEL) ... FAIL
test_pwd (__main__.TestFEL) ... ok
test_quote_keyword (__main__.TestFEL) ... ok
test_semicolon (__main__.TestFEL) ... ok
test_semicolon_chain (__main__.TestFEL) ... ok
test_semicolon_exception (__main__.TestFEL) ... ok
test_singlequotes (__main__.TestFEL) ... ok
test_sort (__main__.TestFEL) ... ok
test_sort_r (__main__.TestFEL) ... ok
test_sort_stdin (__main__.TestFEL) ... ok
test_sort_uniq (__main__.TestFEL) ... ok
test_splitting (__main__.TestFEL) ... FAIL
test_substitution (__main__.TestFEL) ... ok
test_substitution_app (__main__.TestFEL) ... FAIL
test_substitution_doublequotes (__main__.TestFEL) ... ok
test_substitution_insidearg (__main__.TestFEL) ... FAIL
test_substitution_keywords (__main__.TestFEL) ... ok
test_substitution_semicolon (__main__.TestFEL) ... FAIL
test_substitution_sort_find (__main__.TestFEL) ... FAIL
test_substitution_splitting (__main__.TestFEL) ... ok
test_tail (__main__.TestFEL) ... ok
test_tail_n0 (__main__.TestFEL) ... ok
test_tail_n5 (__main__.TestFEL) ... ok
test_tail_n50 (__main__.TestFEL) ... ok
test_tail_stdin (__main__.TestFEL) ... ok
test_uniq (__main__.TestFEL) ... ok
test_uniq_i (__main__.TestFEL) ... ok
test_uniq_stdin (__main__.TestFEL) ... ok
test_unsafe_ls (__main__.TestFEL) ... FAIL

======================================================================
FAIL: test_output_redirection (__main__.TestFEL)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "system_test/tests.py", line 424, in test_output_redirection
    self.assertEqual(result, "foo")
AssertionError: '' != 'foo'
+ foo

======================================================================
FAIL: test_output_redirection_overwrite (__main__.TestFEL)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "system_test/tests.py", line 431, in test_output_redirection_overwrite
    self.assertEqual(result, "foo")
AssertionError: '' != 'foo'
+ foo

======================================================================
FAIL: test_pipe_chain_sort_uniq (__main__.TestFEL)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "system_test/tests.py", line 496, in test_pipe_chain_sort_uniq
    self.assertEqual(result, ["AAA", "BBB", "CCC"])
AssertionError: Lists differ: ['AAA', 'BBB', 'AAA', 'CCC'] != ['AAA', 'BBB', 'CCC']

First differing element 2:
'AAA'
'CCC'

First list contains 1 additional elements.
First extra element 3:
'CCC'

- ['AAA', 'BBB', 'AAA', 'CCC']
?                -------

+ ['AAA', 'BBB', 'CCC']

======================================================================
FAIL[已知待修复]: test_pipe_uniq (__main__.TestFEL)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "system_test/tests.py", line 478, in test_pipe_uniq
    self.assertEqual(result, ["AAA", "BBB", "AAA"])
AssertionError: Lists differ: [''] != ['AAA', 'BBB', 'AAA']

First differing element 0:
''
'AAA'

Second list contains 2 additional elements.
First extra element 1:
'BBB'

- ['']
+ ['AAA', 'BBB', 'AAA']

```
jaobsenyc@JaobsenYc:/mnt/f/OneDrive/OneDrive - University College London/UCL/COMP0010/comp0010-shell-python-p6$ python3 src/shell.py -c "echo aaa > dir1/file2.txt; cat dir1/file1.txt dir1/file2.txt | uniq -i"
Traceback (most recent call last):
  File "src/shell.py", line 22, in <module>
    out = seq.accept(visitor)
  File "/mnt/f/OneDrive/OneDrive - University College London/UCL/COMP0010/comp0010-shell-python-p6/src/abstract_syntax_tree.py", line 110, in accept
    return visitor.visitPipe(self)
  File "/mnt/f/OneDrive/OneDrive - University College London/UCL/COMP0010/comp0010-shell-python-p6/src/visitor.py", line 191, in visitPipe
    outLeft = left.accept(self)
  File "/mnt/f/OneDrive/OneDrive - University College London/UCL/COMP0010/comp0010-shell-python-p6/src/abstract_syntax_tree.py", line 98, in accept
    return visitor.visitSeq(self)
  File "/mnt/f/OneDrive/OneDrive - University College London/UCL/COMP0010/comp0010-shell-python-p6/src/visitor.py", line 181, in visitSeq
    outLeft = left.accept(self)
  File "/mnt/f/OneDrive/OneDrive - University College London/UCL/COMP0010/comp0010-shell-python-p6/src/abstract_syntax_tree.py", line 86, in accept
    return visitor.visitCall(self, input=input)
  File "/mnt/f/OneDrive/OneDrive - University College London/UCL/COMP0010/comp0010-shell-python-p6/src/visitor.py", line 173, in visitCall
    redirectOut.accept(self, stdin=out)
  File "/mnt/f/OneDrive/OneDrive - University College London/UCL/COMP0010/comp0010-shell-python-p6/src/abstract_syntax_tree.py", line 66, in accept
    return visitor.visitRedirectOut(self)
  File "/mnt/f/OneDrive/OneDrive - University College London/UCL/COMP0010/comp0010-shell-python-p6/src/visitor.py", line 108, in visitRedirectOut
    while len(stdin) > 0:
TypeError: object of type 'NoneType' has no len()

```

======================================================================

FAIL[已知]: test_splitting (__main__.TestFEL)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "system_test/tests.py", line 593, in test_splitting
    self.assertEqual(result, "abc")
AssertionError: 'a b c' != 'abc'

- a b c
?  - -
+ abc

> echo a"b"c' 传给app的是 ['a', 'b', 'c']
> 但app理论应该接受的是['abc']

======================================================================

FAIL: test_substitution_app (__main__.TestFEL)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "system_test/tests.py", line 551, in test_substitution_app
    self.assertEqual(result, "foo")
AssertionError: '' != 'foo'
+ foo

======================================================================
FAIL: test_substitution_insidearg (__main__.TestFEL)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "system_test/tests.py", line 515, in test_substitution_insidearg
    self.assertEqual(result, "aaa")
AssertionError: 'a a\n a' != 'aaa'
+ aaa- a a
-  a

======================================================================
FAIL: test_substitution_semicolon (__main__.TestFEL)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "system_test/tests.py", line 539, in test_substitution_semicolon
    self.assertEqual(result, "foo bar")
AssertionError: 'bar' != 'foo bar'
- bar
+ foo bar


======================================================================
FAIL: test_substitution_sort_find (__main__.TestFEL)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "system_test/tests.py", line 533, in test_substitution_sort_find
    self.assertEqual(result, ["AAA", "AAA", "aaa"])
AssertionError: Lists differ: [''] != ['AAA', 'AAA', 'aaa']

First differing element 0:
''
'AAA'

Second list contains 2 additional elements.
First extra element 1:
'AAA'

- ['']
+ ['AAA', 'AAA', 'aaa']

======================================================================
FAIL: test_unsafe_ls (__main__.TestFEL)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "system_test/tests.py", line 470, in test_unsafe_ls
    self.assertEqual(result, "AAA")
AssertionError: '' != 'AAA'
+ AAA

----------------------------------------------------------------------
Ran 66 tests in 134.535s

FAILED (failures=10)
jaobsenyc@JaobsenYc:/mnt/f/OneDrive/OneDrive - University College London/UCL/COMP0010/comp0010-shell-python-p6$