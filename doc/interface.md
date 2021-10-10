# Command Line Interface

COMP0010 Shell should be executed in a Docker container. To build a container image (let's call it `shell`), run

    docker build -t shell .

To execute the shell in interactive mode, run

    docker run -it --rm shell /comp0010/sh

To execute the shell in non-interactive mode (to evaluate a specific command such as `echo foo`), run

    docker run --rm shell /comp0010/sh -c 'echo foo'

To execute unit tests, run

    docker run -p 80:8000 -ti --rm shell /comp0010/tools/test

Then, the results of unit testing will be available at [http://localhost](http://localhost)

To execute code analysis, run

    docker run -p 80:8000 -ti --rm shell /comp0010/tools/analysis

Then, the results of code analysis will be available at [http://localhost](http://localhost)

To execute test coverage, run

    docker run -p 80:8000 -ti --rm shell /comp0010/tools/coverage

Then, the results of coverage computation will be available at [http://localhost](http://localhost)

To execute system tests, your first need to build a Docker image named `comp0010-system-test`:

    docker build -t comp0010-system-test .

Then, execute system tests using the following command (Python 3.7 or higher is required):

    python system_test/tests.py -v

Individual system tests (e.g. `test_cat`) can be executed as

    python system_test/tests.py -v TestShell.test_cat
