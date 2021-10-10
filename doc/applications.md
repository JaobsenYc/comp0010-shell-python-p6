# Applications

COMP0010 Shell provides implementations of widely-used UNIX applications: [cd](https://en.wikipedia.org/wiki/Cd_(command)), [pwd](https://en.wikipedia.org/wiki/Pwd), [ls](https://en.wikipedia.org/wiki/Ls), [cat](https://en.wikipedia.org/wiki/Cat_(Unix)), [echo](https://en.wikipedia.org/wiki/Echo_(command)), [head](https://en.wikipedia.org/wiki/Head_(Unix)), [tail](https://en.wikipedia.org/wiki/Tail_(Unix)), [grep](https://en.wikipedia.org/wiki/Grep), [find](https://en.wikipedia.org/wiki/Find_(Unix)), [sort](https://en.wikipedia.org/wiki/Sort_(Unix)), [uniq](https://en.wikipedia.org/wiki/Uniq), [cut](https://en.wikipedia.org/wiki/Cut_(Unix)), and also their unsafe versions. 

Compared to most UNIX shells, COMP0010 Shell has some important differences in handling applications:

- Applications are executed inside the shell process, rather than new separate processes.
- Applications throw exceptions instead of using exit codes and stderr.
- Applications do not read stdin directly from keyboard, but can only receive it from redirections or pipelines. If an application expects data from stdin, but it is not provided, the application should throw an exception.

## pwd

Outputs the current working directory followed by a newline.

    pwd

## cd

Changes the current working directory.

    cd PATH

- `PATH` is a relative path to the target directory.

## ls

Lists the content of a directory. It prints a list of files and directories separated by tabs and followed by a newline. Ignores files and directories whose names start with `.`.

    ls [PATH]

- `PATH` is the directory. If not specified, list the current directory.

## cat

Concatenates the content of given files and prints it to stdout:

    cat [FILE]...

- `FILE`(s) is the name(s) of the file(s) to contatenate. If no files are specified, uses stdin.

## echo

Prints its arguments separated by spaces and followed by a newline to stdout:

    echo [ARG]...

## head

Prints the first N lines of a given file or stdin. If there are less than N lines, prints only the existing lines without raising an exception.

    head [OPTIONS] [FILE]

- `OPTIONS`, e.g. `-n 15` means printing the first 15 lines. If not specified, prints the first 10 lines.
- `FILE` is the name of the file. If not specified, uses stdin.

## tail

Prints the last N lines of a given file or stdin. If there are less than N lines, prints only the existing lines without raising an exception.

    tail [OPTIONS] [FILE]

- `OPTIONS`, e.g. `-n 15` means printing the last 15 lines. If not specified, prints the last 10 lines.
- `FILE` is the name of the file. If not specified, uses stdin.

## grep

Searches for lines containing a match to the specified pattern. The output of the command is the list of lines. Each line is printed followed by a newline.

    grep PATTERN [FILE]...

- `PATTERN` is a regular expression in [PCRE](https://en.wikipedia.org/wiki/Perl_Compatible_Regular_Expressions) format.
- `FILE`(s) is the name(s) of the file(s). When multiple files are provided, the found lines should be prefixed with the corresponding file paths and colon symbols. If no file is specified, uses stdin.

## cut

Cuts out sections from each line of a given file or stdin and prints the result to stdout.

    cut OPTIONS [FILE]

- `OPTION` specifies the bytes to extract from each line:
    - `-b 1,2,3` extracts 1st, 2nd and 3rd bytes.
    - `-b 1-3,5-7` extracts the bytes from 1st to 3rd and from 5th to 7th.
    - `-b -3,5-` extracts the bytes from the beginning of line to 3rd, and from 5th to the end of line.
- `FILE` is the name of the file. If not specified, uses stdin.

## find

Recursively searches for files with matching names. Outputs the list of relative paths, each followed by a newline.

    find [PATH] -name PATTERN

- `PATTERN` is a file name with some parts replaced with `*` (asterisk).
- `PATH` is the root directory for search. If not specified, uses the current directory.

## uniq

Detects and deletes adjacent duplicate lines from an input file/stdin and prints the result to stdout.

    uniq [OPTIONS] [FILE]

- `OPTIONS`:
    - `-i` ignores case when doing comparison (case insensitive)
- `FILE` is the name of the file. If not specified, uses stdin.

## sort

Sorts the contents of a file/stdin line by line and prints the result to stdout.

    sort [OPTIONS] [FILE]

- `OPTIONS`:
    - `-r` sorts lines in reverse order
- `FILE` is the name of the file. If not specified, uses stdin.

## Unsafe applications

In COMP0010 Shell, each application has an unsafe variant. An unsafe version of an application is an application that has the same semantics as the original application, but instead of raising exceptions, it prints the error message to its stdout. This feature can be used to prevent long sequences from terminating early when some intermediate commands fail. The names of unsafe applications are prefixed with `_`, e.g. `_ls` and `_grep`.
