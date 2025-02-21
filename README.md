# Ten8t: A `Linting` Framework For Infrastructure

`Ten8t` (ten-eighty) lets you create `linting tools` or `design rule checkers` for any task by utilizing
a declarative style similar to `pytest`. It isn't for code, it is for infrastructure, files, folders,
databases, project tracking etc. If you track many files, folders, logs, databases, websites or the
contents of spreadsheets, PDF, csv files, `ten8t` can simplify the task by letting you write
`pytest` like rules.

## Overview

`Ten8t` is a framework that offers a solution monitoring files, folders, projects etc. It works similar to how
`pylint` finds problems in code. I envisioned a tool capable of extending this functionality
across diverse workflows with minimal setup. With a few `check` functions you can easily automate checking
and generate json data ready to be used as an API, incorporated into a streamlit dashboard or into your code.

The intention is NOT to be a `linter` by parsing the syntax of a programming language, it is meant to be a `linter`
in the sense that some system has a large set of rules that must be met for the system to be in a good state. The
more rules the system adheres to the 'better' it is.

After experimenting with various approaches, including straight application scripting and the extensive
configuration files, I found that a `pytest`-like framework could offer the flexibility and ease of use
I sought by offering a simple declarative style.

For larger projects there are attributes that may be assigned to all of your check functions to allow you
fine-grained control over running your checks. For small projects you don't even bother, for large projects
the tags, levels, phases can all be very useful to running just the tests you care about.

When running your checks against your project `ten8t` allows you to generate scores. By default, each check
counts as 1 "point" and all the points are added up to a score which is reported as a percentage. If you
have more detailed needs you have a lot of control over this mechanism.

## Why Not pytest, Great Expectations or other popular tools?

The distinction between `Ten8t`, `pytest`, and Great Expectations and others lies in their scope, complexity, and
target audience.

### pytest:

- **Scope**: Primarily focused on code testing within the Python ecosystem.
- **Complexity**: Comprehensive and feature-rich, tailored for developers and integrated into IDEs.
- **Audience**: Consumed by developers, requiring a code-first approach.
- **Visibility**: Limited to `assert True, msg='...'` while most messages are meant to be hidden.

### Great Expectations (ge):

- **Scope**: Centered around data validation and expectation testing in data pipelines and notebooks.
- **Complexity**: Robust and feature-rich, catering to data scientists and integrated into data pipelines.
- **Audience**: Consumed by data scientists, emphasizing a data-first approach.
- **Visibility** Very good view of data integrity at the rule level.

### Tableaux/PowerBI

- **Scope** Centered around graphical output of charts, graphs, and status for corporate dash-boarding.
- **Complexity** Robust and feature rich catering to real time charting with complex graphical displays.
- **Audience** Consumed by everyone in an organization created as mostly in a low-code environment.
- **Visibility** Beautiful charting. For our application this is eye candy.

### Ten8t:

- **Scope**: Offers comprehensive linting and testing capabilities for any task or system focused on granular pass fail
  tests.
- **Complexity**: Lightweight and straightforward, designed for end users needing detailed testing results and scoring.
- **Audience**: Consumed by end users across various domains, facilitating rule-based testing with clear insights into
  testing results. A typical go/no-go test has 100's of tests that are run almost exclusively as pass/fail
- **Visibility**: Concise list of passing and failing rules with extensive detail and filtering capabilities for
  infrastructure,
  data integrity, project management and general system status.

## Getting Started with Ten8t

If you're familiar with `pytest`, getting started with `ten8t` is a breeze. If you're accustomed to writing tests
with modules starting with "test" and functions beginning with "test",
transitioning to `ten8t` will feel natural. Additionally, if you understand fixtures, you'll find that the concept is
also available through environments. Rule may be tagged with attributes to allow tight control over running checks.

### Simple Rules

You can start with simple rules that don't even reference `ten8t` directly by returning or yielding a boolean value.

```python
from junk import get_drive_space


def check_boolean():
    return get_drive_space('/foo') > 1_000_000_000


def check_yielded_values():
    yield get_drive_space('/foo') > 1_000_000_000
    yield get_drive_space('/fum') > 1_000_000_000
```

As you might expect running this will provide 3 passing test results (assuming the drive space is available)
but with very limited feedback.

You can up your game and return status information by returning or yielding `Ten8tResults`.

```python
from ten8t import Ten8tResult, BR
from junk import get_drive_space


def check_boolean():
    return Ten8tResult(status=get_drive_space('/foo') > 1_000_000_000, msg="Drive space check for foo")


def check_yielded_values():
    yield BR(status=get_drive_space('/foo') > 1_000_000_000, msg="Drive space check for foo")
    yield BR(status=get_drive_space('/fum') > 1_000_000_000, msg="Drive space check for fum")
```

As you might expect running this will also provide 3 passing test results with better messages.

Now we can add more complexity. Tag check functions with attributes to allow subsets of checks to be run. Below
two functions are given different tags. When you make calls to run checks you can specify which tags
you want to allow to run.

```python
from ten8t import Ten8tResult, attributes
import datetime as dt
import pathlib


@attributes(tag="file_exist")
def check_file_exists():
    """ Verify this that my_file exists """
    status = pathlib.Path("my_file.csv").exists()
    return Ten8tResult(status=status, msg="Verify daily CSV file exists")


@attributes(tag="file_age")
def check_file_age():
    file = pathlib.Path("my_file.csv")
    modification_time = file.stat().st_mtime
    current_time = dt.datetime.now().timestamp()
    file_age_in_seconds = current_time - modification_time
    file_age_in_hours = file_age_in_seconds / 3600
    if file_age_in_hours < 24:
        return Ten8tResult(status=True, msg="The file age is OK {file_age_in_hours}")
    else:
        return Ten8tResult(status=False, msg="The file is stale")
```

And even a bit more complexity pass values to these functions using environments, which are similar to `pytest`
fixtures. Ten8t detects functions that start with "env_" and calls them prior to running the check functions.
It builds an environment that can be used to pass parameters to check functions. Typically, things like database
connections, filenames, config files are passed around with this mechanism.

```python
import datetime as dt
import pathlib
from ten8t import attributes, Ten8tResult


def env_csv_file():
    env = {'csv_file': pathlib.Path("my_file.csv")}
    return env


@attributes(tag="file")
def check_file_exists(csv_file):
    """ Verify this that my_file exists """
    return Ten8tResult(status=csv_file.exists(), msg="Verify daily CSV file exists")


@attributes(tag="file")
def check_file_age(csv_file):
    modification_time = csv_file.stat().st_mtime
    current_time = dt.datetime.now().timestamp()
    file_age_in_seconds = current_time - modification_time
    file_age_in_hours = file_age_in_seconds / 3600
    if file_age_in_hours < 24:
        return Ten8tResult(status=True, msg="The file age is OK {file_age_in_hours}")
    else:
        return Ten8tResult(status=False, msg="The file is stale")
```

## How is Ten8t Organized?

A common use case is to have check-functions saved in python code files that python can discover via the import
mechanism allowing files to be more or less, automatically detected.

Ten8t uses the following hierarchy:

    Ten8tPackage` (one or more Ten8tModules in a folder)
        Ten8tModule` (one or more Ten8tFunctions in a Python file (function starting with the text "check_"))
            Ten8tFunction` (when called will return 0 or more `Ten8tResults`)

Typically one works at the module or package level where you have python files that have 1 or more files with rules in
them.

Each `Ten8tFunction` returns/yields 0-to-N results from its generator function. By convention, if None is returned, the
rule
was skipped.
The rule functions that you write don't need to use generators. They can return a variety of output
(e.g., Boolean, List of Boolean, `Ten8tResult`, List of `Ten8tResult`), or you can write a generator that yields
results as they are checked.

Alternatively you can ignore the file and folder discovery mechanism provide list of rules as regular python
functions and `Ten8t` will happily run them for you if pass a list of check functions the make a `Ten8tChecker`

```python
import ten8t
from rules import rule1, rule2, rule3, rule4, rule5, sql_conn

checker = ten8t.Ten8tChecker(check_functions=[rule1, rule2, rule3, rule4, rule5], auto_setup=True)
results = checker.run_all(env={'db': sql_conn, 'cfg': 'cfg.json'})
```

## Rule Integrations

To simplify getting started, there are included rules you can call to check files and folders on your file system
dataframes, Excel spreadsheets, PDF files and web APIs. These integrations make many common checks just a few lines of
code.

These generally take the form of you wrapping them in some way to provide the required inputs and any attributes
required by your app as well as messages specific to your application.

The rules shown below trigger errors if there are any log files > 100k in length and if they haven't been updated
in the last 5 minutes.

```python
import ten8t


@ten8t.attributes(tag="tag")
def check_rule1():
    for folder in ['folder1', 'folder2', 'folder3']:
        yield from ten8t.rule_large_files(folder=folder, pattern="log*.txt", max_size=100_000)


@ten8t.attributes(tag="tag")
def check_rule2():
    for folder in ['folder1', 'folder2', 'folder3']:
        yield from ten8t.rule_stale_files(folder=folder, pattern="log*.txt", minutes=5.0)


@ten8t.attributes(tag="tag")
def check_rule3(cfg):
    """cfg: application config file."""
    for folder in cfg['logging']['folders']:
        yield from ten8t.rule_stale_files(folder=folder, pattern="log*.txt", minutes=5.0)
```

## What is the output?

The low level output of a `Ten8tFunction` are `Ten8tResults`. Each `Ten8tResult` is trivially converted to a `json`
record or a line in a CSV file for processing by other tools. It is easy to connect things up to
`Streamlit`, `FastAPI` or a `typer` CLI app by json-ifying the results. Each test can have a lot of data attached
to it, if needed, but from the end user perspective the `msg` and `status` are often enough. You will notice that
there are useful elements in the result including the doc string of the rule function, which allows you to provide
documentation for your rules that is exposed all the way up result stack. For example your doc strings could
include information useful providing detailed information and greatly simplify displaying metadata in UI elements
like tooltips as well as detailed error information with the traceback and exception data.

```json
{
  "result": {
    "status": true,
    "func_name": "check_result_1_1",
    "pkg_name": "",
    "module_name": "check_1",
    "msg": "Result for test 1.1",
    "info_msg": "",
    "warn_msg": "",
    "doc": "Check result 1.1 docstring",
    "runtime_sec": 0.00027108192443847656,
    "except_": "None",
    "traceback": "",
    "skipped": false,
    "weight": 100,
    "tag": "tag1",
    "level": 1,
    "phase": "prototype",
    "count": 1,
    "ruid": "1_1",
    "ttl_minutes": 0,
    "mit_msg": "",
    "owner_list": []
  }
}
```

## What are scores?

The idea of scoring is simple but the details are complex. Scores let you look at the results of all of your checks
and reduce it to number from 0 to 100. A simple percentage of pass fail results can work...but what if some rules are "
easy" while others are hard? What if some test have 100's of ways to fail (each line in a spreadsheet needs a comment)
but has only one result when there are no failures? It turns out you need weights and ways to aggregate results to
make sense of these things.

Out of the box, most of these cases can be handled by choosing a scoring method. Currently, scoring happens globally,
but it is in work creating scoring by function.

| Scoring              | Description                                                              |
|----------------------|--------------------------------------------------------------------------|
| `by_result`          | Each result from a function counts as 100%                               |
| `by_function_binary` | All tests from a single function must pass to get 100% for the function. |
| `by_funciton_mean`   | If a function has 3 results and 2 pass the function result is 66%        |
| `binary_fail`        | If any single result from a function is False, the function score is 0%  |
| `binary_pass`        | If any single result from a function is True, the function score is 100% |

In addition to the scoring, each function has a weight that is also applied to it after the scoring to all
different rules to have higher weights.

The utility of this is somewhat useless in smaller systems (< 100 rules) since we generally are aiming to
have 100% pass.

## What are @attributes?

Each rule function can be assigned attributes that define metadata about the rule function. Attributes are at the heart
of how `ten8t` allows you to filter, sort, select tests to run and view by adding decorators to your check functions.

| Attribute        | Description                                                                                                                         |
|------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| `tag`            | Zero or more strings that can be used for filtering results.                                                                        |
| `phase`          | A single string that indicates a project phase like testing or development.                                                         |
| `level`          | A numeric value that is better for greater than/less than tests.                                                                    |
| `weight`         | A positive number indicating the weight of a functions results. The nominal weight is 100.                                          |
| `skip`           | Indicates the function should be skipped.                                                                                           |
| `ruid`           | Rule-ID is a unique identifier for a rule.                                                                                          |
| `ttl_minutes`    | Allow caching of results so expensive tests don't need to be rerun which is only useful in cases where you run tests over and over. |
| `finish_on_fail` | Aborts processing of `ten8t` function on the first failure.                                                                         |
| `skip_on_none `  | If an environment parameter has a None value then the function will be skipped.                                                     |
| `fail_on_none`   | If an environment parameter has a None value then the function will be failed.                                                      |
| `thread_id`      | Any function can be assigned a thread to run in to take advantage of concurrency.                                                   |           

## What are Rule-Ids (RUIDS)?

Tags and phases are generic information that is only present for filtering. The values don't mean much to the inner
workings of `ten8t`.  `RUID`s are different. The purpose of a `RUID` is to tag every rule function with a unique value
that is, ideally, meaningful to the user. For very large rule sets this becomes prohibitive and ends up looking like
integers with some leading text. The only rule to the code is that they are unique. If you tag a single
function with an RUID the system will expect you to put a unique ID on every function, or to set the `auto_ruid` flag
to True when creating a `Ten8tChecker` object.

What do you get for this? You now have fine grain control to the function level AND the user level to enable/disable
checks. A `pylint` analogy is that you can turn off-line width checks globally for you project setting values in
the `.lintrc` file. In the case of `ten8t`, perhaps part of your system has one set of rules and another part of
the system has the same set but some don't apply.
Or perhaps in an early phase development a subset of rules is applied, and at another a different set of rules is
applied.

RUIDS allow you to set function level granularity with "simple" config files.

RUIDs can be anything hashable (but come on, they should be short strings). Smart-ish values like File-001, Fill-002, '
smarter' or File-Required, File-Too-Old. Whatever makes sense on the project. As a general rule smart naming conventions
aren't smart, so beware of the bed you make for yourself.

```python
from ten8t import attributes, Ten8tResult
import pathlib


@attributes(ruid="file_simple")
def check_file_age():
    f = pathlib.Path("/user/file1.txt")
    return Ten8tResult(status=f.exists(), msg=f"File {f.name}")


@attributes(ruid="file_complex")
def check_file_age():
    f = pathlib.Path("/user/file2.txt")
    return Ten8tResult(status=f.exists(), msg=f"File {f.name}")
```

## Threading  (PROVISIONAL MAY CHANGE)

It is possible to assign a thread ID to anny `Ten8t` function using the standard attribute mechanism. For larger
rulesets this can speed things up, the current implementations has you pass a checker object to the thead runner
which manages putting all the functions in their own thread and collecting results. At this time the code
supports threading using so IO bound code should work better. This is not a silver bullet, you still need to
write rules that don't have dependencies with global state. If you have database connections there should be
one for each thread that needs it.

The current mechanism is to create a checker object like you normally do, but pass that object to a
`Ten8yThread` object that manages finding all the functions for each thread and running things as
needed. For many use cases enabling multi threading is as easy as giving a thread id to your check functions.

In the test suite we run 100 of these in parallel.

```python
import pathlib
from ten8t import Ten8tResult, attributes, Ten8tThread, Ten8tChecker


@attributes(ruid="file_complex", thread_id='thread1')
def function1():
    f = pathlib.Path("/user/file1.txt")
    return Ten8tResult(status=f.exists(), msg=f"File {f.name}")


@attributes(ruid="file_complex", thread_id='thread2')
def function2():
    f = pathlib.Path("/user/file2.txt")
    return Ten8tResult(status=f.exists(), msg=f"File {f.name}")


@attributes(ruid="file_complex", thread_id='thread3')
def function3():
    f = pathlib.Path("/user/file3.txt")
    return Ten8tResult(status=f.exists(), msg=f"File {f.name}")


checker = Ten8tChecker(check_functions=[function1, function2, function3], auto_setup=True)
tcheck = Ten8tThread(checker, max_workers=4)  # take checker object and put functions in their own threads
results = tcheck.run_all()  # now using the thread runner object.
```

## Ten8t RC

A `.ten8trc` file can be provided in the `.TOML`, `.XML`, `.JSON` format, or from code as a dictionary. I hope you don't
need to use `XML`.

RC files allow you to set up matching expressions for tags, phases, ruids and levels. Python regular expressions
are allowed, so there is a lot of power available to make rules that are hard to read. The website https://regex101.com
is recommended for testing your regular expressions.

Give a list of each of the attributes. Any item that starts with a dash is an exclusion rule. Anything that doesn't
start with a dash is an inclusion rule.

__If there are no inclusion rules then EVERYTHING is included__
__If there are no exclusion rules then NOTHING is excluded__

There are several common patterns:

1) Do nothing (empty rc file or dictionary) to run EVERYTHING.
2) Only list exclusions. Useful in cases where you are testing several things that are mostly similar.
3) Use tags, phases and selectors to run subsets of your tests.
4) You can completely punt and ONLY use ruids and regular expressions. Super powerful, but you need to plan well.

```text
NOTE: Tags and ruids should NOT contain spaces.  Don't do it and don't ask for it.  The idea is that they
      are short and easily added to lists.  Also you are allowed to say:
      
      tags = "t1 t2 t3"
      
      instead of typing:
      
      tags = ['t1', 't2','t3']
      
      It is just easier to type and to read and to get right.
```

### Some examples:

```toml
[package1]
tags = ['t1']
phases = ['p1']
```

The above rc file only runs phase p1 and tag t1 rules.

```toml
[package1]
tags = ['-t1']
phases = ['-p1', '-p2']
```

This one runs any rule that isn't `t1` and isn't `p1` or `p2`.

```toml
[package1]
ruids = ['file.*']
```

This rc only runs `ruid`s that start with `file`

## TTL Time to Live Caching

If you are running checks in real-ish-time you may want to throttle some check functions. TTL allows caching of results
to reduce execution of long-running checks.

Just tag the check function with the `ttl_minutes` attribute, and it will use cached results if the call frequency is
inside the TTL that was specified. This feature is useful in situations where you are `ten8t`ing a system
in real time for things like dashboards or long-running tasks. You don't need to check a 20MB log file for exceptions
every minute. When you need TTL, it is very useful.

The status during the TTL period will be the __last result that ran__. At startup, everything will run since the caches
are empty.

NOTE: `ttl_minutes` is assumed to be in minutes, should you provide a number without units. If you want hours days or
seconds you can put the units in the string ("30sec", "1day", ".5 hours")

```python
from ten8t import attributes, Ten8tResult
from kick_astro import make_black_hole_image


@attributes(ttl_minutes="1.0hr")
def check_file_age():
    pic = make_black_hole_image()
    yield Ten8tResult(status=pic.black_hole_exists(), msg="Hourly cluster image generation check")
```

## How can these rules be organized?

Lots of ways.

1) Just give it a bunch of functions in a list would work. Ideally they each return `Ten8tResults`.
2) Point it to a file and `ten8t` will find all the functions that start with`check` and call them. (`ten8t_module`)
3) Point it to a folder (or pass it a bunch of filenames) and ten8t will load each module and collect all the tests (
   `ten8t_package`)

## How are environments used?

Environments in `ten8t` are analogous to fixtures in `pytest` but the use-case is different.
The machinations of supporting all the scopes is not necessary in this case. You provide
a set of named environment variables, and they are used as parameters to any functions that need them.

Ten8t makes all lists, dictionaries, dataframes and sets that are passed as part of an environment
immutable-ish in order to reduce the possibility of modifying the state of the environment.

Any functions in a module that start with `env` are considered environment functions, and they
will be called with the current global environment and are expected to return additions being made
to that environment. The global environment is provided, so you can see everything rather than
making putting all the parameters in the function signature.

Note that the variable names in the dictionary are the parameters that are passed to the function.

```python
import ten8t
import pandas as pd


def env_setup(_: dict) -> dict:
    # Auto-detected function that starts with "env_".  This function
    # should return a dictionary of values that can be used as parameters
    # to functions in this (and other) modules.

    module_env = {'db_config': 'sqlite.sql',
                  'number_config': 42,
                  'data_frame': pd.DataFrame()}
    return module_env


def check_global(global_env):
    """This value is pulled from another module """
    yield ten8t.TR(status=global_env == "hello", msg=f"Got global env={global_env}")


def check_env1(db_config):
    """Should pick up db config from local env"""
    yield ten8t.TR(status=db_config == 'sqlite.sql', msg=f"Got db_config as string {db_config}")


def check_env2(number_config):
    """Should pick up db config from local env"""
    yield ten8t.TR(status=number_config == 42, msg=f"Got number {42}")
```

## Logging

`ten8t` supports opt in logging. If you do nothing, nothing will get logged. A setup function is
provided that lets you write to your own log and/or propagate to system level logging.

```python
import logging
import ten8t as t8

# Setup t8 logging to log messages along with whatever the application is doing
t8.ten8t_setup_logging(level=logging.DEBUG)
```

```python
import logging
import ten8t as t8

# Setup t8 logging of t8 message to a file and (by default propagate to the system)
t8.ten8t_setup_logging(level=logging.DEBUG, file_name="./t8.log")
```

```python
import logging
import ten8t as t8

# Setup t8 logging of t8 messages and NOT propagating those messages to the root logger.
t8.ten8t_setup_logging(level=logging.DEBUG, file_name="./t8.log", propagate=False)
```

```python
import logging
import ten8t as t8
from sys import stderr

# Setup t8 logging of message to the console
t8.ten8t_setup_logging(level=logging.DEBUG, stream=stderr, propagate=False)
```

## Typer Command Line Demo App For `ten8t_cli`:

Included is a light weight `typer` app that allows to point `ten8t` at a file or folder and check the rules via the
command
line.

To run it against any folder

`python -m ten8t_cli.py --pkg path/to/package_folder`

To run it against a folder and start a FastAPI endpoint do:

`python -m ten8t_cli.py --pkg path/to/package_folder --api --port 8000`

```shell
>>>python ten8t_cli.py --help 
                                                                                                                                                                                                                                                                                              
 Usage: ten8t_cli.py [OPTIONS]                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                              
 Run Ten8t checks on a given package or module from command line.                                                                                                                                                                                                                             
 
╭─ Options ──────────────────────────────────────────────────────────────────────────────╮
│ --mod      -m      TEXT     The module to run rules against. [default: None]           │
│ --pkg              TEXT     The package to run rules against. [default: None]          │
│ --json     -j      TEXT     The JSON file to write results to. [default: None]         │
│ --flat     -f               Should the output be flat or a hierarchy.                  │
│ --score    -s               Print the score of the rules.                              │
│ --api      -a               Start FastAPI.                                             │
│ --port     -p      INTEGER  FastAPI Port [default: 8000]                               │
│ --verbose  -v               Enable verbose output.                                     │
│ --help                      Show this message and exit.                                │
╰────────────────────────────────────────────────────────────────────────────────────────╯

```

## FastAPI Interface Demo

To integrate your rule checking results with a web API using `FastAPI`, you can refer to the `ten8t_cli.py` file for a
straightforward approach to creating a `FastAPI` app from your existing code. No changes are required in your code to
support a `FastAPI` interface. If you have created `rule_id`s for all of your rule functions, they will all be
accessible via the API. Alternatively, if you haven't used `rule_id`s, you can run the entire set of
functions or filter by `tag`, `level` or `phase`. The sample command-line app serves as a simple example
of how to connect a `ten8t` ruleset to the web via FastAPI.

Integration with `FastAPI` is simple since it utilizes Python dicts for result data.
The `ten8t_cli` demo tool demonstrates that this can be achieved with just a few lines of code to
create a FastAPI interface.

Simply run the command with the `--api` flag, and you'll see `uvicorn` startup your API. Go to
http://localhost:8000/docs to see the API.

```
/Users/chuck/ten8t/.venv/bin/python ten8t_cli.py --pkg . --api 
INFO:     Started server process [3091]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:64116 - "GET / HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:64116 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:64116 - "GET /openapi.json HTTP/1.1" 200 OK
```

And going to `localhost:8000/docs` gets you this:

FastAPI swagger interface:
![FastAPI](./img/fastapi2.png)

FastAPI example running some rules:
![FastAPI](./img/fastapi.png)

## Streamlit Demo

Integration with `streamlit` was important, so I made the way you interact with `ten8t` work well with the
tools that `streamlit` exposes. Integrating with the goodness of `streamlit` is a breeze.
Here is a non-trivial example showing many of the features of `ten8t` in a `streamlit` app.  
in 200 lines of code you can select from packages folders, have a full streamlit UI to select the package, tags,
levels, ruids and generate colored tabular report.

Here is the setup using a couple of modules in a package folder:

![Streamlit](./img/streamlit_allup.png)

## TOX

Python 3.10 to 3.12 and soon to be 3.13. Python 3.9 was dropped for type hinting support using |.

```text
.pkg: _exit> python /Users/chuck/Projects/ten8t/.venv1/lib/python3.12/site-packages/pyproject_api/_backend.py True poetry.core.masonry.api
  py310: OK (18.07=setup[6.71]+cmd[11.36] seconds)
  py311: OK (14.76=setup[3.78]+cmd[10.98] seconds)
  py312: OK (14.76=setup[3.62]+cmd[11.14] seconds)
  lint: OK (15.47=setup[2.83]+cmd[12.63] seconds)
  congratulations :) (63.07 seconds)
```

## Pyproject TOML

In order to build the project you need to use will need to use some form of keyring in order to extract
the required secrets. Something like:

## Lint

```text
------------------------------------------------------------------
Your code has been rated at 9.79/10 (previous run: 9.77/10, +0.01)
```

## WTH does `Ten8t` mean and HTH do you say it?

`Ten8t` is a [numeronym](https://en.wikipedia.org/wiki/Numeronym) for the word 1080 (ten-eighty). Why was this
chosen...because the first things I picked that were not packages on pypi were "too close" to existing package
names. I spent more time that I care to admit coming up with different names. It refers to skiing or
snowboarding tricks involving 3 rotations.

The preferred way for using `ten8t` in code is to say:

```python
import ten8t as t8
```

Please pronounce the `t8` as `tee eight` (as in an early prototype for
a [T-800](https://en.wikipedia.org/wiki/T-800_(character))) *NOT* `tate`.

## TODO

1. Improve threading

## Latest changes

1. Updated for dependabot.
