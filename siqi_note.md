python3 system_test/tests.py -v TestFEL.test_cat

Agile
* Dynamic Dispatch
* Design Pattern

* Singleton (lazy version, thread safe ver, double locking ver) --> don't use
Factory --> 1. extend libraries or frameworks 2. don't know object type beforehead
Builder --> create object with a lot attributes step by step
Decorator 
Adapter

Observer 
Visitor:
1. When you need to perform an operation on all elements of a tree of objects
2. Clean up the business logic of auxiliary behaviors
3. When a behavior makes sense only in some classes of a class hierarchy, but not in others
Strategy
Template

* Python Iterator

* Refactor
* Code Smell: Duplicate codes, Shotgun Surgery, Long parameter list
* Anti Pattern: Magic Number, Error hiding, Circle-ellipse problem

* Documentation

* Testing
unit -> integration -> system
white-box testing
mutation 

* code coverage
atatement, branch, path

----------

* Quote(https://www.gnu.org/software/bash/manual/html_node/Quoting.html)
* Glowing(https://teaching.idallen.com/cst8207/15w/notes/190_glob_patterns.html): 
Wildcard pattern 

* abstract class: super()
* interface: duck typing

---------

* test_cat
    AssertionError: Lists differ: ['<operators.Expression object at 0x7f767d8[78 chars]CCC'] != ['AAA', 'BBB', 'AAA', 'CCC']

* test_cat_stdin
