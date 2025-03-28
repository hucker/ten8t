# Ten8t: Observability for Filesystems, APIs, Databases, Documents and more.

<!-- Pytest status is honor system based on running pytest/tox prior to push to GitHub -->
![Ten8t PyTest Status](https://img.shields.io/badge/PyTest-899/899-brightgreen.svg)
&nbsp;&nbsp;
![Ten8t Coverage Status](https://img.shields.io/badge/Coverage-90%25-brightgreen.svg)
&nbsp;&nbsp;
[![Python](https://img.shields.io/pypi/pyversions/ten8t)](https://pypi.org/project/ten8t/)
&nbsp;&nbsp;
[![Documentation Status](https://readthedocs.org/projects/ten8t/badge/?version=latest)](https://ten8t.readthedocs.io/en/latest/)
&nbsp;&nbsp;
![Downloads](https://img.shields.io/pypi/dm/ten8t)
<br>
![Stars](https://img.shields.io/github/stars/hucker/ten8t)
&nbsp;&nbsp;
![Last Release](https://img.shields.io/github/commits-since/hucker/ten8t/latest?include_prereleases)
&nbsp;&nbsp;
![GitHub Release Date](https://img.shields.io/github/release-date-pre/hucker/ten8t)
&nbsp;&nbsp;
![GitHub Release](https://img.shields.io/github/v/release/hucker/ten8t?include_prereleases)

`Ten8t` (pronounced "ten-eighty") is a framework for managing observability and rule-based checks across
files, folders, APIs, spreadsheets, and projects. Drawing inspiration from tools like `pytest` and `pylint`, `Ten8t`
makes simple tasks easy while providing the flexibility to tackle more complex scenarios as needed. By allowing you
to write reusable, declarative rules, `Ten8t` lets you monitor and validate information systems. Whether it’s a
quick check of a file’s existence or enforcing hundreds of granular rules for system health and data integrity.

`Ten8t` can be thought of as a tool to build a "linter" for your infrastructure, file systems, databases,
and documents. It is designed to be very efficient to set up rules to check and outputs in python data or
JSON make integrating with common tools straight forward. Non-trival examples with streamlit, typer, rich,
FastAPI and textual that development can be low friction. "Standard" rules are available out of the box,
but it is easy to write python code to verify anything you like. It enables you to define customized pass/fail
checks and organize them using tags, attributes, and phases for fine-grained control. With support for
lightweight setup and scalability, `Ten8t` works for small projects and large, complex systems. Its intuitive
tooling ensures that basic tests are easy to write, while its extensibility with standard Python code within
reach of your coding ability.

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

- **Scope**: Focused on testing filesystem, files, SQL, API access and custom coded python checks.
- **Complexity**: Designed for to be light weight for developers to check things quickly and repeatably.
- **Audience**: This tool is a framework for infrastructure developers needing a tool to be the backbone of your
  observability. Since the output is directly available as JSON it is very easy to integrate.
- **Visibility**: `ten8t` generats JSON. INtegration samples are included for `streamlit`, `FastAPI`, `textual` and
  `typer`.

## Getting Started with Ten8t

If you're familiar with `pytest`, getting started with `ten8t` is a breeze. If you're accustomed to writing tests
with modules starting with "test" and functions beginning with "test",
transitioning to `ten8t` will feel natural. Additionally, if you understand fixtures, you'll find that the concept is
also available through environments. Rule may be tagged with attributes to allow tight control over running checks.

### A modest checker...

The very simplest thing you cand do with `ten8t` takes a few functions, gives them to the
a checker object and then tells that object to run all the functions, collect the results. This is the core.
Everything that follows from here is window dressing to make this test engine run.

```python
import ten8t as t8
import pathlib


def check_foo():
  """Check if a foo exists"""
  return pathlib.Path("./foo.txt").exists()


def check_fum():
  """Check if a fum exists"""
  return pathlib.Path("./fum.txt").exists()


# A checker object collections your functions up, runs them all and hands you back results.
results = t8.Ten8tChecker(check_functions=[check_foo, check_fum]).run_all()


```

As you might expect, a framework could discover these tests provide 2 passing test results if the files all exist.

In order to be useful we need functions that return more detail and ideally functions that return more than
one `Ten8tResult`. So we support yield and a result object that stores...everyting I could think of.

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

As you might expect running this will also provide 3 passing test results with richer data using the TR object. Note
that these functions yield results rather than return them and some tags have been added, foreshadowing that you
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
connections, filenames, config files are passed around with this mechanism. Note that in multi threading checking
some variables may not be shared across threads. File names, lists of strings and integers (and anything hashable)
work fine, but sharing a SQL connection across threads won't work.

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

Once you have your check functions written you need to set up a `Ten8tChecker` object to run them.
Essentially you need to pass the checker all of your check functions so they can be run.

A common use case is to have check-functions saved in python source files that `ten8t` can discover via
the import mechanism allowing check-functions in files to be auto-detected like `pytest`.

Ten8t uses the following hierarchy:

    Ten8tPackage` (one or more Ten8tModules in a folder)
        Ten8tModule` (one or more Ten8tFunctions in a Python file (function starting with the text "check_"))
            Ten8tFunction` (when called will return 0 or more `Ten8tResults`)

Typically one works at the module or package level where you have python files that have 1 or more functions in them
and you have collections of files to make packages. Note that `ten8t` a module is 1 file and a package is a folder
with atleast one file that has a check function. Similare to python but not exact.

Each `Ten8tFunction` returns/yields 0-to-N results from its generator function. By convention, if None is returned, the
rule was skipped.

The rule functions that you write don't need to use generators. They can return a variety of output
(e.g., Boolean, List of Boolean, `Ten8tResult`, List of `Ten8tResult`), or you can write a generator that yields
results as they are checked. Canonical form is that you yield, but `ten8t` is tolerant, but returning booleans
and depending on using your function name and your docstrings for error mssages is on you!

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


checker = t8.Ten8tChecker(check_functions=[rule1, rule2, rule3, rule4], env={'data': [1, 2, 3, 4]})
results = checker.run_all()
```

This example shows a bunch of rules that are passed in some of which might need a single sql connection object.

## Rule Integrations

To simplify getting started, there are included rules you can call to check files and folders on your file system
dataframes, Excel spreadsheets, PDF files and web APIs. These integrations make many common checks just a
few lines of code.

These generally take the form of you wrapping them up with data specific to your system.

The rules shown below trigger errors if there are any log files > 100k in length and if they haven't been updated
in the last 5 minutes using rules from based on the `pathlib` packages

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

There are a handful of useful packages built into `ten8t`. You don't need to do anything special to use them
beyond pip installing their dependencies. They detect what you have installed on your system and the rules
will be made available. So if you have `ping3` installed, then the rules in for `ping3` will be available.

This package uses `narwhals` to handle data frames. If you have pandas or polars installed the rules
for dataframes should work for you (e.g., `ten8t` is dependent on narwhals not `pandas`/`polars`)

If you want to add rules for common usecases PRs are welcomed. See `rule_files.py` and `rule_ping.py`.

| Package Name | GitHub Repository Link                                                               |
|--------------|--------------------------------------------------------------------------------------|
| fs           | [GitHub - PyFilesystem/pyfilesystem2](https://github.com/PyFilesystem/pyfilesystem2) |
| narwhals     | [GitHub - thousandoaks/narwhals](https://github.com/thousandoaks/narwhals)           |
| pathlib      | Python `pathlib` package                                                             |
| pdf          | [GitHub - camelot-dev/camelot](https://github.com/camelot-dev/camelot)               |
| ping         | [GitHub - kyan001/ping3](https://github.com/kyan001/ping3)                           |
| requests     | [GitHub - psf/requests](https://github.com/psf/requests)                             |
| sqlalchemy   | [GitHub - sqlalchemy/sqlalchemy](https://github.com/sqlalchemy/sqlalchemy)           |

If you aren't sure what has been detected when loading `ten8t` run this code in the REPL. If the name is
in the `whats_installed` string then `ten8t` detected that you have pip installed the right tools.

```text
>>> import ten8t
>>> ten8t.__version__
'0.0.21'
>>> ten8t.whats_installed()
'fs,narwhals,openpyxl,pathlib,pdf,ping,requests,sqlalchemy'
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


<!--file snippets/result.json-->
```json
{
    "package_count": 1,
    "module_count": 1,
    "modules": [
        "check_file_system"
    ],
    "function_count": 4,
    "tags": [
        "folder"
    ],
    "levels": [
        1
    ],
    "phases": [
        "proto"
    ],
    "ruids": [
        "f1",
        "f2",
        "file1",
        "file2"
    ],
    "score": 100.0,
    "env_nulls": [],
    "start_time": "2025-03-21 06:54:17.586919",
    "end_time": "2025-03-21 06:54:17.587155",
    "duration_seconds": 0.000236,
    "functions": [],
    "passed_count": 6,
    "warn_count": 0,
    "failed_count": 0,
    "skip_count": 0,
    "total_count": 6,
    "check_count": 4,
    "result_count": 6,
    "clean_run": true,
    "perfect_run": true,
    "abort_on_fail": false,
    "abort_on_exception": false,
    "results": [
        {
            "status": true,
            "func_name": "check_files_f1",
            "pkg_name": "",
            "module_name": "check_file_system",
            "msg": "The path <<code>>../examples/file_system/folder1/file1.txt<</code>> does exist.",
            "info_msg": "",
            "warn_msg": "",
            "msg_rendered": "The path ../examples/file_system/folder1/file1.txt does exist.",
            "doc": "Simple always passing function",
            "runtime_sec": 5.507469177246094e-05,
            "except_": "None",
            "traceback": "",
            "skipped": false,
            "weight": 100.0,
            "tag": "folder",
            "level": 1,
            "phase": "proto",
            "count": 1,
            "ruid": "file1",
            "ttl_minutes": 0.0,
            "mit_msg": "",
            "owner_list": [],
            "skip_on_none": false,
            "fail_on_none": false,
            "summary_result": false,
            "thread_id": "main_thread__"
        },
        {
            "status": true,
            "func_name": "check_files_f1",
            "pkg_name": "",
            "module_name": "check_file_system",
            "msg": "The path <<code>>../examples/file_system/folder1/file2.txt<</code>> does exist.",
            "info_msg": "",
            "warn_msg": "",
            "msg_rendered": "The path ../examples/file_system/folder1/file2.txt does exist.",
            "doc": "Simple always passing function",
            "runtime_sec": 1.621246337890625e-05,
            "except_": "None",
            "traceback": "",
            "skipped": false,
            "weight": 100.0,
            "tag": "folder",
            "level": 1,
            "phase": "proto",
            "count": 2,
            "ruid": "file1",
            "ttl_minutes": 0.0,
            "mit_msg": "",
            "owner_list": [],
            "skip_on_none": false,
            "fail_on_none": false,
            "summary_result": false,
            "thread_id": "main_thread__"
        },
        {
            "status": true,
            "func_name": "check_files_f2",
            "pkg_name": "",
            "module_name": "check_file_system",
            "msg": "The path <<code>>../examples/file_system/folder2/file1.txt<</code>> does exist.",
            "info_msg": "",
            "warn_msg": "",
            "msg_rendered": "The path ../examples/file_system/folder2/file1.txt does exist.",
            "doc": "Simple always passing function",
            "runtime_sec": 1.8835067749023438e-05,
            "except_": "None",
            "traceback": "",
            "skipped": false,
            "weight": 100.0,
            "tag": "folder",
            "level": 1,
            "phase": "proto",
            "count": 1,
            "ruid": "file2",
            "ttl_minutes": 0.0,
            "mit_msg": "",
            "owner_list": [],
            "skip_on_none": false,
            "fail_on_none": false,
            "summary_result": false,
            "thread_id": "main_thread__"
        },
        {
            "status": true,
            "func_name": "check_files_f2",
            "pkg_name": "",
            "module_name": "check_file_system",
            "msg": "The path <<code>>../examples/file_system/folder2/file2.txt<</code>> does exist.",
            "info_msg": "",
            "warn_msg": "",
            "msg_rendered": "The path ../examples/file_system/folder2/file2.txt does exist.",
            "doc": "Simple always passing function",
            "runtime_sec": 1.0013580322265625e-05,
            "except_": "None",
            "traceback": "",
            "skipped": false,
            "weight": 100.0,
            "tag": "folder",
            "level": 1,
            "phase": "proto",
            "count": 2,
            "ruid": "file2",
            "ttl_minutes": 0.0,
            "mit_msg": "",
            "owner_list": [],
            "skip_on_none": false,
            "fail_on_none": false,
            "summary_result": false,
            "thread_id": "main_thread__"
        },
        {
            "status": true,
            "func_name": "check_folder1",
            "pkg_name": "",
            "module_name": "check_file_system",
            "msg": "The path <<code>>../examples/file_system/folder1<</code>> does exist.",
            "info_msg": "",
            "warn_msg": "",
            "msg_rendered": "The path ../examples/file_system/folder1 does exist.",
            "doc": "Simple always passing function",
            "runtime_sec": 1.0013580322265625e-05,
            "except_": "None",
            "traceback": "",
            "skipped": false,
            "weight": 100.0,
            "tag": "folder",
            "level": 1,
            "phase": "proto",
            "count": 1,
            "ruid": "f1",
            "ttl_minutes": 0.0,
            "mit_msg": "",
            "owner_list": [],
            "skip_on_none": false,
            "fail_on_none": false,
            "summary_result": false,
            "thread_id": "main_thread__"
        },
        {
            "status": true,
            "func_name": "check_folder2",
            "pkg_name": "",
            "module_name": "check_file_system",
            "msg": "The path <<code>>../examples/file_system/folder2<</code>> does exist.",
            "info_msg": "",
            "warn_msg": "",
            "msg_rendered": "The path ../examples/file_system/folder2 does exist.",
            "doc": "Simple always passing function",
            "runtime_sec": 1.3113021850585938e-05,
            "except_": "None",
            "traceback": "",
            "skipped": false,
            "weight": 100.0,
            "tag": "folder",
            "level": 1,
            "phase": "proto",
            "count": 1,
            "ruid": "f2",
            "ttl_minutes": 0.0,
            "mit_msg": "",
            "owner_list": [],
            "skip_on_none": false,
            "fail_on_none": false,
            "summary_result": false,
            "thread_id": "main_thread__"
        }
    ]
}
```
<small>result.json &nbsp;&nbsp; 06:54:17 2025-03-21</small>

<!--file end-->

In addition to the json output, which has all data a set of serialization tools are included that allow for output
in CSV, markdown and Excel formats. These tools are "easily" extended or modified by looking at the code in the
`serialize` sub package. Do note that `render` is used for formatting single lines of result data, while serialization
is used for exporting the entire results of a generated when running `checker.run_all()`.

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

![FastAPI Demo](docs/_static/fastapi.png)

## Streamlit Demo  (`ten8t/st_ten8t/st_demo.py`)

Integration with `streamlit` was important, so I made the way you interact with `ten8t` work well with the
tools that `streamlit` exposes. Integrating with the goodness of `streamlit` is a breeze. Here is a non-trivial
example showing many of the features of `ten8t` in a `streamlit` app. In 200 lines of code you can select from
packages folders, have a full streamlit UI to select the package, tags,levels, ruids and generate colored
tabular report.

Here is the setup using a couple of modules in a package folder:

![Streamlit Demo](docs/_static/streamlit_allup.png)

## Rich Demo (`ten8t/rich_ten8t`)

Here is a example of connecting `ten8t` up to the rich package using the progress bar object to
move a progress bar, and the rich table and some emojis to make a tabular output.

It is worth noting here that there are 4 progress bar steps, but there are 6 results. Is this a bug?
No. It is not possible to reliably count the number of checks that will be performed before running
the checker. This is because check functions can yield many results. What we can count is the number
of functions that have been registered, so progress is given in functions run not yields...yielded.

![Rich Demo](docs/_static/rich_demo.png)

## Textual Demo

The folder `textual_ten8t` has a demonstration app showing `ten8t` integration with `textual` by supporting
the same `examples` folder used in other demos. This demo shows how logging, checking, and basic interactions with
`ten8t` are performed. Because `ten8t` supports `rich` formatting the messages generated by checking functions are
displayed as formatted text.

If you know `Textual` this demo should get you well on your way.

The `--folder`/`-f` option allows you to pass in a root folder for the textual file system viewer. This
capability allows you to use the demo app as a development tool since it gives a flexible way to look at
packages and modules and run them independently. The default is the current working directory. While this is
just a demo, it is quite useful in that you can rapidly test your rule sets interactively.

![Textual Demo](docs/_static/textual_demo.png)

## TOX

Python 3.10, 3.11, 3.12 and 3.13.

```text
2025-03-17 14:48:54 [INFO] pytest_logger: Global pytest logger initialized.
.pkg: _exit> python /Users/chuck/Projects/ten8t/.venv/lib/python3.13/site-packages/pyproject_api/_backend.py True poetry.core.masonry.api
  py313: OK (16.88=setup[5.55]+cmd[11.33] seconds)
  py310: OK (16.59=setup[3.94]+cmd[12.65] seconds)
  py311: OK (14.60=setup[3.04]+cmd[11.56] seconds)
  py312: OK (17.77=setup[4.81]+cmd[12.95] seconds)
  lint: OK (14.19=setup[2.91]+cmd[11.29] seconds)
  congratulations :) (80.06 seconds)
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
mypy, pypi, tox, pytest, coverage, code metrics and readthedocs. It's a useful, non-trivial test bed.

## Code Metrics (from radon)

The code metrics section contains the output from running the python tool [Radon](https://github.com/rubik/radon)
against all the files in the ten8t package folder. The metrics all come with a rank (except Halstead, which I googled
for
reasonable values). Anything less than **C** is suspect. For the most part the code is all A's and B's though
`ten8t_checker` and `ten8t_function` have issues as these are the most complex code where lots of "magic"
happens getting everything to work flexibly for end users.

Interestingly the radon grading system for maintainability gave everything an A (as of 0.0.20). The checker
and function modules had the lowest scores, while the other metrics hit pretty hard and gave C's
and F's. My preference is the Halstead metrics as those appear to be far more sensitive...and those are the ones
I needed to Google/ChatGPT for thresholds. The bugs and time columns seem to be the most sensitive. I think it
is reasonable to target bad code with these tools, it isn't perfect, but I know that `ten8t_function.py` and
`ten8t_checker.py` are the most complicated and neglected classes given that many small and not so small
features have been bolted on over time while most of the other class are the leafs in the project that are easier
to apply "separation of concerns" to. It is safe to say most of the magic happens in these two places.

PR's for classes and files with low scores are welcomed.

__Halstead__
<!--file snippets/radon_hal.csv-->

| File                | Bugs | Difficulty | Effort  | Time   | Bugs<br>Rank | Difficulty<br>Rank | Effort<br>Rank | Time<br>Rank |
|---------------------|------|------------|---------|--------|--------------|--------------------|----------------|--------------|
| ten8t_attribute.py  | 0.08 | 6.00       | 1483.05 | 82.39  | B            | A                  | B              | B            |
| ten8t_checker.py    | 0.47 | 6.50       | 9149.36 | 508.30 | F            | A                  | D              | F            |
| ten8t_exception.py  | 0.00 | 0.00       | 0.00    | 0.00   | A            | A                  | A              | A            |
| ten8t_filter.py     | 0.03 | 2.00       | 159.45  | 8.86   | A            | A                  | A              | A            |
| ten8t_function.py   | 0.18 | 6.68       | 3660.46 | 203.36 | C            | A                  | C              | D            |
| ten8t_immutable.py  | 0.00 | 0.00       | 0.00    | 0.00   | A            | A                  | A              | A            |
| ten8t_inirc.py      | 0.00 | 0.50       | 1.00    | 0.06   | A            | A                  | A              | A            |
| ten8t_jsonrc.py     | 0.00 | 0.00       | 0.00    | 0.00   | A            | A                  | A              | A            |
| ten8t_logging.py    | 0.00 | 0.50       | 1.00    | 0.06   | A            | A                  | A              | A            |
| ten8t_module.py     | 0.06 | 5.36       | 1025.19 | 56.95  | B            | A                  | B              | B            |
| ten8t_package.py    | 0.03 | 1.64       | 124.60  | 6.92   | A            | A                  | A              | A            |
| ten8t_progress.py   | 0.07 | 3.12       | 633.74  | 35.21  | B            | A                  | A              | A            |
| ten8t_rc.py         | 0.02 | 1.65       | 122.11  | 6.78   | A            | A                  | A              | A            |
| ten8t_rc_factory.py | 0.01 | 1.88       | 42.11   | 2.34   | A            | A                  | A              | A            |
| ten8t_result.py     | 0.03 | 2.71       | 232.47  | 12.92  | A            | A                  | A              | A            |
| ten8t_ruid.py       | 0.03 | 3.75       | 378.84  | 21.05  | A            | A                  | A              | A            |
| ten8t_thread.py     | 0.01 | 1.00       | 15.51   | 0.86   | A            | A                  | A              | A            |
| ten8t_tomlrc.py     | 0.00 | 0.00       | 0.00    | 0.00   | A            | A                  | A              | A            |
| ten8t_util.py       | 0.06 | 3.55       | 664.73  | 36.93  | B            | A                  | A              | A            |
| ten8t_xmlrc.py      | 0.00 | 0.50       | 2.38    | 0.13   | A            | A                  | A              | A            |
| ten8t_yield.py      | 0.17 | 4.67       | 2420.79 | 134.49 | C            | A                  | C              | C            |

<small>radon_hal.csv &nbsp;&nbsp; 16:35:57 2025-03-27</small>

<!--file end-->



__Maintainability__
<!--file snippets/radon_mi.csv-->

| File                | Maint.<br>Index | Rank |
|---------------------|-----------------|------|
| ten8t_attribute.py  | 70.20           | A    |
| ten8t_checker.py    | 27.50           | A    |
| ten8t_exception.py  | 100.00          | A    |
| ten8t_filter.py     | 68.20           | A    |
| ten8t_function.py   | 51.80           | A    |
| ten8t_immutable.py  | 100.00          | A    |
| ten8t_inirc.py      | 95.20           | A    |
| ten8t_jsonrc.py     | 100.00          | A    |
| ten8t_logging.py    | 89.50           | A    |
| ten8t_module.py     | 62.80           | A    |
| ten8t_package.py    | 71.70           | A    |
| ten8t_progress.py   | 62.40           | A    |
| ten8t_rc.py         | 70.20           | A    |
| ten8t_rc_factory.py | 77.00           | A    |
| ten8t_result.py     | 64.30           | A    |
| ten8t_ruid.py       | 78.20           | A    |
| ten8t_thread.py     | 63.90           | A    |
| ten8t_tomlrc.py     | 100.00          | A    |
| ten8t_util.py       | 69.70           | A    |
| ten8t_xmlrc.py      | 85.80           | A    |
| ten8t_yield.py      | 47.50           | A    |

<small>radon_mi.csv &nbsp;&nbsp; 16:35:57 2025-03-27</small>

<!--file end-->

__Complexity__
<!--file snippets/radon_cc.csv-->

| File               | Name                  | Rank | Complexity |
|--------------------|-----------------------|------|------------|
| ten8t_checker.py   | Ten8tChecker          | A    | 5.00       |
| ten8t_exception.py | Ten8tTypeError        | A    | 1.00       |
| ten8t_exception.py | Ten8tValueError       | A    | 1.00       |
| ten8t_exception.py | Ten8tException        | A    | 1.00       |
| ten8t_function.py  | Ten8tFunction         | B    | 7.00       |
| ten8t_immutable.py | Ten8tEnvList          | A    | 2.00       |
| ten8t_immutable.py | Ten8tEnvDict          | A    | 2.00       |
| ten8t_immutable.py | Ten8tEnvSet           | A    | 1.00       |
| ten8t_inirc.py     | Ten8tIniRC            | A    | 3.00       |
| ten8t_jsonrc.py    | Ten8tJsonRC           | A    | 3.00       |
| ten8t_module.py    | Ten8tModule           | A    | 4.00       |
| ten8t_package.py   | Ten8tPackage          | A    | 3.00       |
| ten8t_progress.py  | Ten8tLogProgress      | A    | 4.00       |
| ten8t_progress.py  | Ten8tDebugProgress    | A    | 3.00       |
| ten8t_progress.py  | Ten8tMultiProgress    | A    | 3.00       |
| ten8t_progress.py  | Ten8tProgress         | A    | 2.00       |
| ten8t_progress.py  | Ten8tNoProgress       | A    | 2.00       |
| ten8t_rc.py        | Ten8tRC               | B    | 6.00       |
| ten8t_result.py    | Ten8tResult           | A    | 3.00       |
| ten8t_thread.py    | Ten8tThread           | A    | 3.00       |
| ten8t_tomlrc.py    | Ten8tTomlRC           | A    | 3.00       |
| ten8t_util.py      | NextIntValue          | A    | 2.00       |
| ten8t_xmlrc.py     | Ten8tXMLRC            | A    | 5.00       |
| ten8t_yield.py     | Ten8tYield            | A    | 5.00       |
| ten8t_yield.py     | Ten8tYieldPassOnly    | A    | 2.00       |
| ten8t_yield.py     | Ten8tYieldFailOnly    | A    | 2.00       |
| ten8t_yield.py     | Ten8tYieldPassFail    | A    | 2.00       |
| ten8t_yield.py     | Ten8tYieldAll         | A    | 2.00       |
| ten8t_yield.py     | Ten8tYieldSummaryOnly | A    | 2.00       |
| ten8t_yield.py     | Ten8tNoResultSummary  | A    | 1.00       |

<small>radon_cc.csv &nbsp;&nbsp; 16:35:57 2025-03-27</small>

<!--file end-->

## TODO

1. Improve ten8t_checker.py and ten8t_function.py to reduce their complexity numbers.
2. Add support for handling coroutines and async generators, so ten8t can support all function types.
2. Progress bars for using multithreading is broken.

## Latest changes

1. Added a textual demo.
2. Added explicit error messages for async check functions
2. Added support for csv/markdown/excel output from the checker.
