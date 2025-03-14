## Ten8t: Observability for Filesystems, APIs, Databases, Documents and more.

<!-- Pytest status is honor system based on running pytest/tox prior to push to GitHub -->
![Ten8t PyTest Status](https://img.shields.io/badge/PyTest-865/865-brightgreen.svg)
&nbsp;&nbsp;
![Ten8t Coverage Status](https://img.shields.io/badge/Coverage-90%25-brightgreen.svg)
&nbsp;&nbsp;
[![Python](https://img.shields.io/pypi/pyversions/ten8t)](https://pypi.org/project/ten8t/)
&nbsp;&nbsp;
[![Documentation Status](https://readthedocs.org/projects/ten8t/badge/?version=latest)](https://ten8t.readthedocs.io/en/latest/)
&nbsp;&nbsp;
![Downloads](https://img.shields.io/pypi/dm/ten8t)

`Ten8t` (pronounced "ten-eighty") is a framework for managing observability and rule-based checks across
files, folders, APIs, spreadsheets, and projects. Drawing inspiration from tools like `pytest` and `pylint`, `Ten8t`
makes simple tasks easy while providing the flexibility to tackle more complex scenarios as needed. By allowing you
to write reusable, declarative rules, `Ten8t` lets you monitor and validate information systems. Whether it’s a
quick check of a file’s existence or enforcing hundreds of granular rules for system health and data integrity.

`Ten8t` can be thought of as a "linter" for your infrastructure many "standard" rules are available out of the box,
but it is easy to write python code to verify anything you like. It enables you to define customized pass/fail checks
and organize them using tags, attributes, and phases for fine-grained control. With support for lightweight setup
and scalability, `Ten8t` works for small projects and large, complex systems. Its intuitive tooling
ensures that basic tests are easy to write, while its extensibility with standard Python code within reach of
your coding ability.


## Why Not pytest, Great Expectations or other popular tools?

The distinction between `Ten8t`, `pytest`, and Great Expectations and others lies in their scope, complexity, and
target audience.

### pytest:

- **Scope**: Focused on source code testing within the Python ecosystem.
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

- **Scope**: Focused on testing filesystem, file and generic python checks.
- **Complexity**: Lightweight and straightforward, designed for developers to get check functions up quickly.
- **Audience**: This tool is a framework for infrastructure developers needing a tool to be the backbone of your
  observability. Since the output is directly available as JSON it is very easy to integrate.
- **Visibility**: Sample apps are included that run Streamlit, FastAPI and typer.

## Getting Started with Ten8t

If you're familiar with `pytest`, getting started with `ten8t` is a breeze. If you're accustomed to writing tests
with modules starting with "test" and functions beginning with "test",
transitioning to `ten8t` will feel natural. Additionally, if you understand fixtures, you'll find that the concept is
also available through environments. Rule may be tagged with attributes to allow tight control over running checks.

### Simple Rules

You can start with simple rules that don't even reference `ten8t` directly by returning or yielding boolean values.
Here are some simple check functions.

```python

import pathlib


def check_boolean():
   return pathlib.Path("./foo").exists()


def check_yielded_values():
    return [pathlib.Path("./foo").exists(), pathlib.Path("./fum").exists()]
```

As you might expect, a framwork could discover these tests provide 3 passing test results if the files all exist.

You can up your game and return status information by returning or yielding `Ten8tResults`.

```python
from ten8t import TR, attributes
import pathlib

#NOTE TR is an alias for Tent8tResult.  Since it is used very often it is useful to have a short version.

@attributes(tag="foo")
def check_boolean():
    yield TR(status=pathlib.Path("./foo").exists(), msg="Folder foo exists")


@attributes(tag="fum")
def check_yielded_values():
    yield TR(status=pathlib.Path("./fum").exists(), msg="Folder foo exists")
    yield TR(status=pathlib.Path("./fum").exists(), msg="Folder fum exists")
```

As you might expect running this will also provide 3 passing test results with richer data using the TR object also note
that these functions yield results rather than return them and some tags have been added, forshadowing that you
will be able to run the "foo" tests or the "fum" tests.

Now we can add more complexity running more complex code. Tag check functions with attributes to allow subsets of checks
to be run. Below
two functions are given different tags. When you make calls to run checks you can specify which tags
you want to allow to run.

```python
from ten8t import attributes, TR
import datetime as dt
import pathlib


@attributes(tag="file_exist")
def check_file_exists():
    """ Verify this that my_file exists """
    status = pathlib.Path("my_file.csv").exists()
    yield TR(status=status, msg="Verify daily CSV file exists")


@attributes(tag="file_age")
def check_file_age():
    file = pathlib.Path("my_file.csv")
    modification_time = file.stat().st_mtime
    current_time = dt.datetime.now().timestamp()
    file_age_in_seconds = current_time - modification_time
    file_age_in_hours = file_age_in_seconds / 3600
    if file_age_in_hours < 24:
        yield TR(status=True, msg="The file age is OK {file_age_in_hours}")
    else:
        yield TR(status=False, msg="The file is stale")
```

And even a bit more complexity pass values to these functions using environments, which are similar to `pytest`
fixtures. Ten8t detects functions that start with "env_" and calls them prior to running the check functions.
It builds an environment that can be used to pass parameters to check functions. Typically, things like database
connections, filenames, config files are passed around with this mechanism.

```python
import datetime as dt
import pathlib
from ten8t import attributes, TR


def env_csv_file():
    env = {'csv_file': pathlib.Path("my_file.csv")}
    return env


@attributes(tag="file")
def check_file_exists(csv_file):
    """ Verify this that my_file exists """
    return TR(status=csv_file.exists(), msg="Verify daily CSV file exists")


@attributes(tag="file")
def check_file_age(csv_file):
    modification_time = csv_file.stat().st_mtime
    current_time = dt.datetime.now().timestamp()
    file_age_in_seconds = current_time - modification_time
    file_age_in_hours = file_age_in_seconds / 3600
    if file_age_in_hours < 24:
        return TR(status=True, msg="The file age is OK {file_age_in_hours}")
    else:
        return TR(status=False, msg="The file is stale")
```

## How is Ten8t Used?

Well, once you have your check functions written you need to set up a `Ten8tChecker` object to run them
for you. Essentially you need to pass the checker all of your check functions so they can be run.

A common use case is to have check-functions saved in python source files that `ten8t` can discover via
the import mechanism allowing files to be more or less, automatically detected.

Ten8t uses the following hierarchy:

    Ten8tPackage` (one or more Ten8tModules in a folder)
        Ten8tModule` (one or more Ten8tFunctions in a Python file (function starting with the text "check_"))
            Ten8tFunction` (when called will return 0 or more `Ten8tResults`)

Typically one works at the module or package level where you have python files that have 1 or more files with rules in
them.

Each `Ten8tFunction` returns/yields 0-to-N results from its generator function. By convention, if None is returned, the
rule was skipped.

The rule functions that you write don't need to use generators. They can return a variety of output
(e.g., Boolean, List of Boolean, `Ten8tResult`, List of `Ten8tResult`), or you can write a generator that yields
results as they are checked. Canonical form is that you yield, but `ten8t` is tolerant.

Alternatively you can ignore the file and folder discovery mechanism and provide a list of rules as regular python
functions and `Ten8t` will happily run them for you when you pass a list of check functions
the make a `Ten8tChecker` object.

```python
import ten8t as t8


def rule1(cfg):
   return 1 in cfg['data']


def rule2(cfg):
   return 2 in cfg['data']


def rule3(cfg):
   return 3 in cfg['data']


def rule4(cfg):
   return 4 in cfg['data']


checker = t8.Ten8tChecker(check_functions=[rule1, rule2, rule3, rule4], auto_setup=True, env={'data': [1, 2, 3, 4]})
results = checker.run_all()
```

This example shows a bunch of rules that are passed in some of which might need a single sql connection object.

## Rule Integrations

To simplify getting started, there are included rules you can call to check files and folders on your file system
dataframes, Excel spreadsheets, PDF files and web APIs. These integrations make many common checks just a
few lines of code.

These generally take the form of you wrapping them up with data specific to your system.

The rules shown below trigger errors if there are any log files > 100k in length and if they haven't been updated
in the last 5 minutes.

```python
import ten8t as t8

@t8.attributes(tag="tag")
def check_rule1():
    for folder in ['folder1', 'folder2', 'folder3']:
        yield from t8.rule_large_files(folder=folder, pattern="log*.txt", max_size=100_000)


@t8.attributes(tag="tag")
def check_rule2():
    for folder in ['folder1', 'folder2', 'folder3']:
        yield from t8.rule_stale_files(folder=folder, pattern="log*.txt", minutes=5.0)


@t8.attributes(tag="tag")
def check_rule3(cfg):
    """cfg: application config file."""
    for folder in cfg['logging']['folders']:
        yield from t8.rule_stale_files(folder=folder, pattern="log*.txt", minutes=5.0)
```

Currently, there are integrations for file access with pathlib, generic file system access with FS,
database with SQLAlchemy, data frames with narwhals and ping with ping3, requests with (duh) requests,
pdf files with camelot and Excel files with openpyxl.

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

For most use-cases scoring is not needed, or just using the default by_result since we are most often using this
in cases were we expect 100% "pass", however for very large rulesets scores becomes more important because there
is always something broken.

## What are @attributes?

Each rule function can be assigned attributes that define metadata about the rule function. Attributes
are at the heart of how `ten8t` allows you to filter, sort, select tests to run and view by adding
decorators to your check functions. For large projects where subsets of rules need to be run and
detailed setup information is required attributes provide a consistent way to tag adorn functions with data.

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
integers with some leading text. The only rule about RUIDs is that they be unique. If you tag a single
function with an RUID the system will expect you to put a unique ID on every function, or to set the `auto_ruid` flag
to True when creating a `Ten8tChecker` object.

What do you get for this? You now have fine grain control to the function level AND the user level to enable/disable
checks. A `pylint` analogy is that you can turn off-line width checks globally for you project setting values in
the `.lintrc` file. In the case of `ten8t`, perhaps part of your system has one set of rules and another part of
the system has the same set but some don't apply.
Or perhaps in an early phase development a subset of rules is applied, and at another a different set of rules is
applied.

RUIDS allow you to set function level granularity with "simple" config files.

RUIDs can be anything hashable (but come on, they should be short strings). Smart-ish values like File-001, Fill-002,
or `File-Required`, `File-Too-Old`. Whatever makes sense on the project. As a general rule smart naming conventions
aren't smart in the long run.

```python
from ten8t import attributes, Ten8tResult
import pathlib


@attributes(ruid="file_simple")
def check_file_age():
    f = pathlib.Path("/user/file1.txt")
    return Ten8tResult(status=f.exists(), msg=f"File {f.name}")


@attributes(ruid="file_complex")
def check_file_age():
    f = pathlib.Path("/user/very_big_file.txt")
    return Ten8tResult(status=f.exists(), msg=f"File {f.name}")
```

## Threading  (PROVISIONAL MAY CHANGE)

It is possible to assign a thread ID to any `Ten8t` function using the standard attribute mechanism. For larger
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
tcheck = Ten8tThread(checker)  # take checker object and put functions in their own threads
results = tcheck.run_all(max_workers=4)  # now using the thread runner object.
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


def make_black_hole_image():
   """Do stuff that takes a really long time."""
   return True


@attributes(ttl_minutes="1.0hr")
def check_file_age():
   status = make_black_hole_image()
   yield Ten8tResult(status=status, msg="Hourly cluster image generation check")
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
import ten8t as t8
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
    yield t8.TR(status=global_env == "hello", msg=f"Got global env={global_env}")


def check_env1(db_config):
    """Should pick up db config from local env"""
    yield t8.TR(status=db_config == 'sqlite.sql', msg=f"Got db_config as string {db_config}")


def check_env2(number_config):
    """Should pick up db config from local env"""
    yield t8.TR(status=number_config == 42, msg=f"Got number {42}")
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
t8.ten8t_setup_logging(level=logging.DEBUG, stream_=stderr, propagate=False)
```

## Typer Command Line Demo App (`ten8t/cli`)

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

## FastAPI Interface Demo (`ten8t/cli`)

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
![FastAPI](docs/_static/fastapi2.png)

FastAPI example running some rules:
![FastAPI](docs/_static/fastapi.png)

## Streamlit Demo  (`ten8t/st_ten8t/st_demo.py`)

Integration with `streamlit` was important, so I made the way you interact with `ten8t` work well with the
tools that `streamlit` exposes. Integrating with the goodness of `streamlit` is a breeze.
Here is a non-trivial example showing many of the features of `ten8t` in a `streamlit` app.  
in 200 lines of code you can select from packages folders, have a full streamlit UI to select the package, tags,
levels, ruids and generate colored tabular report.

Here is the setup using a couple of modules in a package folder:

![Streamlit](docs/_static/streamlit_allup.png)

## Rich Demo (`ten8t/rich_ten8t`)

Here is a simple example of connecting `ten8t` up to the rich package using the progress bar object to
move a progress bar, and the rich table and emojis to make a tabular output.

```text
(ten8t) rich> python rich_demo.py 

Processing Checks ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4/4
                      Test Results                       
┏━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Tag  ┃ RUID  ┃ Function Name ┃ Status ┃ Message       ┃
┡━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ tag1 │ ruid1 │ check1        │   ✅   │ Test 1 passed │
│ tag2 │ ruid2 │ check2        │   ❌   │ Test 2 failed │
│ tag3 │ ruid3 │ check3        │   ✅   │ Test 3 passed │
│ tag3 │ ruid3 │ check3        │   ✅   │ Test 4 passed │
│ tag3 │ ruid4 │ check4        │   ✅   │ Test 5 passed │
│ tag3 │ ruid4 │ check4        │   ✅   │ Test 6 passed │
└──────┴───────┴───────────────┴────────┴───────────────┘
```

## TOX

Python 3.10, 3.11, 3.12 and 3.13.

```text
.pkg: _exit> python /Users/chuck/Projects/ten8t/.venv1/lib/python3.12/site-packages/pyproject_api/_backend.py True poetry.core.masonry.api
  py310: OK (14.53=setup[3.64]+cmd[10.89] seconds)
  py311: OK (13.90=setup[3.25]+cmd[10.65] seconds)
  py312: OK (12.57=setup[1.91]+cmd[10.67] seconds)
  py313: OK (14.83=setup[3.97]+cmd[10.86] seconds)
  lint: OK (12.68=setup[1.88]+cmd[10.81] seconds)
  congratulations :) (68.54 seconds)
```

## Lint

```text
------------------------------------------------------------------
Your code has been rated at 9.79/10 (previous run: 9.79/10, +0.00)
```

## WTH does `Ten8t` and what's with your wierd names?

`Ten8t` is a [numeronym](https://en.wikipedia.org/wiki/Numeronym) for the word 1080 (ten-eighty). Why was this
chosen...because the first things I picked that were not packages on pypi were "too close" to existing package
names. I spent more time that I care to admit coming up with different names. The name refers to skiing or
snowboarding tricks involving 3 rotations.

The preferred way for using `ten8t` in code is to write:

```python
import ten8t as t8

t8.ten8t_logger.info("Hello")
```

or

```python
from ten8t import ten8t_logger

ten8t_logger("Hello")
```

Please pronounce the `t8` as `tee eight` (as in an early prototype for
a [T-800](https://en.wikipedia.org/wiki/T-800_(character))) *NOT* `tate`.

Why is your name `hucker`? It is a portmanteau of Chuck (my name) and hacker with the added benefit
that is a derogatory name for someone who isn't very good at skiing. I'll call it a portmanthree.

## Why does this exist?

This project is a piece of code that is useful to me, and it serves as non-trivial piece of code where
I can experiment with more advanced features in Python that I don't get at my day job. Inspecting code,
advanced yielding, threading, strategy patterns, dynamic function creation, hook functions, decorators,
mypy, pypi, tox, pytest, coverage and readthedocs. It's a useful, non-trivial test bed.


## TODO

1. Add support for handling coroutines and async generators, so ten8t can support all function types.
2. Progress bars for using multithreading is broken.

## Latest changes

1. Added explicit error messages for async check functions
