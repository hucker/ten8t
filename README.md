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

# Ten8t Framework

`Ten8t` (pronounced "ten-eighty") is a framework for observability and rule-based checks across files, folders, APIs,
spreadsheets, and projects. Inspired by `pytest` and `pylint`, it simplifies basic tasks while handling complex
scenarios flexibly. With reusable, declarative rules, Ten8t enables monitoring and validation of information
systems—from simple file existence checks to comprehensive system health verification.

Think of Ten8t as an infrastructure "linter" for file systems, databases, and documents. It enables quick
rule setup with Python data or JSON output for python/web integration. Examples with `streamlit`, `typer`, `rich`,
`FastAPI` and `textual` demonstrate low-friction development. While "standard" rules are available, writing
custom Python verifications is straightforward. Ten8t supports custom pass/fail checks organized with many attributes
for precise filtering control. Its design works for both small projects and complex systems, making basic
tests easy while remaining extensible through standard Python.

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
- **Complexity**: Designed for to be lightweight for developers to check things quickly and repeatably.
- **Audience**: This tool is a framework for infrastructure developers needing a tool to be the backbone of your
  observability. Since the output is directly available as JSON it is very easy to integrate.
- **Visibility**: `ten8t` generates JSON. Integration samples are included for `streamlit`, `FastAPI`, `textual` and
  `typer`.

## Getting Started with Ten8t

If you're familiar with `pytest`, getting started with `ten8t` is a breeze. If you're accustomed to writing tests
with modules starting with "test" and functions beginning with "test",
transitioning to `ten8t` will feel natural. Additionally, if you understand fixtures, you'll find that the concept is
also available through environments. Rule may be tagged with attributes to allow tight control over running checks.

### A modest checker...

The very simplest thing you cand do with `ten8t` takes a few functions, gives them to the checker
object and then tells that object to run all the functions, collect the results. This is the core.
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
one `Ten8tResult`. So we support yield and a result object that stores...everything I could think of.

```python
from ten8t import TR, categories
import pathlib

#NOTE TR is an alias for Tent8tResult.  Since it is used very often it is useful to have a short version.

@categories(tag="foo")
def check_boolean():
    yield TR(status=pathlib.Path("./foo").exists(), msg="Folder foo exists")


@categories(tag="fum")
def check_yielded_values():
    yield TR(status=pathlib.Path("./fum").exists(), msg="Folder foo exists")
    yield TR(status=pathlib.Path("./fum").exists(), msg="Folder fum exists")
```

As you might expect running this will also provide 3 passing test results with richer data using the TR object. Note
that these functions yield results rather than return them and some tags have been added, foreshadowing that you
will be able to run the "foo" tests or the "fum" tests because the check function has be tagged with `categories`.

Now we can add more complexity running more complex code. Tag check functions with `categories` to allow
subsets of checks to be run. Below two functions are given different tags. When you make calls to run
checks you can specify which tags
you want to allow to run.

```python
from ten8t import categories, TR
import datetime as dt
import pathlib

@categories(tag="file_exist")
def check_file_exists():
    """ Verify this that my_file exists """
    status = pathlib.Path("my_file.csv").exists()
    yield TR(status=status, msg="Verify daily CSV file exists")

@categories(tag="file_age")
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
from ten8t import categories, TR


def env_csv_file():
    env = {'csv_file': pathlib.Path("my_file.csv")}
    return env


@categories(tag="file")
def check_file_exists(csv_file):
    """ Verify this that my_file exists """
    return TR(status=csv_file.exists(), msg="Verify daily CSV file exists")


@categories(tag="file")
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

## Threading Support

Threading is supported in various ways. The easiest way to enable threading

```python
import datetime as dt
import pathlib
from ten8t import categories, threading, TR, Ten8tChecker, Ten8tThread


@categories(tag="file")
@threading(thread_id='thread1')
def check_file_exists():
    """ Verify this that my_file exists """
    return TR(status=pathlib.Path('my_file.txt').exists(), msg="Verify daily CSV file exists")


@categories(tag="file")
@threading(thread_id='thread2')
def check_file_age():
  modification_time = pathlib.Path('my_file.txt').stat().st_mtime
    current_time = dt.datetime.now().timestamp()
    file_age_in_seconds = current_time - modification_time
    file_age_in_hours = file_age_in_seconds / 3600
    if file_age_in_hours < 24:
        return TR(status=True, msg="The file age is OK {file_age_in_hours}")
    else:
        return TR(status=False, msg="The file is stale")


ch = Ten8tChecker(check_functions=[check_file_age, check_file_exists])

# Use the Ten8tThread class to run the checker.  
results = Ten8tThread(checker=ch).run_all(max_workers=5)



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

Typically one works at the module or package level where you have python files that have 1 or more functions in them,
and you have collections of files to make packages. Note that `ten8t` a module is 1 file and a package is a folder
with at least one file that has a check function. Similar to python but not exact.

Each `Ten8tFunction` returns/yields 0-to-N results from its generator function. By convention, if None is returned, the
rule was skipped.

The rule functions that you write don't need to use generators. They can return a variety of output
(e.g., Boolean, List of Boolean, `Ten8tResult`, List of `Ten8tResult`), or you can write a generator that yields
results as they are checked. Canonical form is that you yield, but `ten8t` is tolerant, but returning booleans
and depending on using your function name and your docstrings for error messages is on you!

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

You can see here that data is provided externally, but programmatically via the env parameter. Often times
this parameter is directly loaded from a config file, or comes pre-populated with data frames and database
connections.

## Rule Integrations

To simplify getting started, there are included rules you can call to check files and folders on your file system
dataframes, Excel spreadsheets, PDF files and web APIs. These integrations make many common checks just a
few lines of code.

These generally take the form of you wrapping them up with data specific to your system.

The rules shown below trigger errors if there are any log files > 100k in length and if they haven't been updated
in the last 5 minutes using rules from based on the `pathlib` packages

```python
import ten8t as t8


@t8.categories(tag="tag")
def check_rule1():
    for folder in ['folder1', 'folder2', 'folder3']:
        yield from t8.rule_large_files(folder=folder, pattern="log*.txt", max_size=100_000)


@t8.categories(tag="tag")
def check_rule2():
    for folder in ['folder1', 'folder2', 'folder3']:
        yield from t8.rule_stale_files(folder=folder, pattern="log*.txt", minutes=5.0)


@t8.categories(tag="tag")
def check_rule3(cfg):  # <-- Config file has the test setup
    """cfg: application config file."""
    for folder in cfg['logging']['folders']:
        yield from t8.rule_stale_files(folder=folder, pattern="log*.txt", minutes=5.0)
```

There are a handful of useful packages built into `ten8t`. You don't need to do anything special to use them
beyond pip installing their dependencies. They detect what you have installed on your system and the rules
will be made available. So if you have `ping3` installed, then the rules in for `ping3` will be available.

This package uses `narwhals` to handle data frames. If you have pandas or polars installed the rules
for dataframes should work for you (e.g., `ten8t` is dependent on narwhals not `pandas`/`polars`)

If you want to add rules for common use cases PRs are welcomed. See `rule_files.py` and `rule_ping.py`.

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

Here is an example of connecting `ten8t` up to the `rich` package using the progress bar object to
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

# Development Philosophy

This project serves as both a practical tool and a playground for advanced Python features I don't
encounter in my day job: code inspection, advanced yielding, threading, strategy patterns, dynamic
function creation, hooks, decorators, mypy, github, pypi, tox, pytest integrtion, coverage metrics, dynamically
created readme and readthedocs.

As it evolved, tests have proven invaluable. They give me confidence
to perform major architectural changes, confirming everything works when tests pass. TDD genuinely
saves significant time.

TDD complements YAGNI principles in my development approach. Rather than creating extensive object
systems upfront, I build classes incrementally, only refactoring when the existing abstraction no
longer supports clean design. This contrasts with my early career tendency to build elaborate
frameworks for functionality that never materialized.


## Philosophy

I designed the API to prioritize flexibility and user experience. Rather than requiring strict parameter
formats, the library intelligently handles various input types to save users time and reduce friction.

The API accepts multiple formats for common inputs:

1) Lists of strings can be passed as space-delimited strings (`"foo fum quux"`), single values (`"foo"`),
   conventional lists (`["foo"]`), or even empty values (`""`, `[]`, `None`)
2) File paths work with both strings (`"file.txt"`) and Path objects (`pathlib.Path("file.txt")`)
3) When a list is expected but a single item is provided, the API automatically wraps it in a list

This approach simplifies integration with configuration files and command-line options by reducing data
transformation code. While this diverges from strict typing practices, it significantly improves developer
experience and speeds up implementation.

If there's demand, I may introduce strict variants of these interfaces in the future.

## Code Metrics (from `radon`)

I track code quality using [Radon](https://github.com/rubik/radon) metrics across the `ten8t` package.
In general, the codebase maintains good quality scores with mostly A's and B's.

The columns below have been sorted worst to best. It can be seen that most of the complexity is in the
`ten8t_checker`/`function`/`yield` modules as those are the most complex functionality in the system and
they are reliably at the top of all of these metrics. This is where the paid is.

Pull requests addressing code quality in lower-scoring files are welcome...actually any PR's are welcome.

NOTE: Restructuring occurred recently made the flat architecture more hierarchical, where classes that were
subclassed were made into subprojects and files were split up in to folders and sub folders
(see folders progress/rc/render/score/serialize) At this time those files are not visible in this listing.

__Halstead__
<!--file snippets/radon_hal.csv-->

| File               | Bugs | Difficulty | Effort  | Time   | Bugs<br>Rank | Difficulty<br>Rank | Effort<br>Rank | Time<br>Rank |
|--------------------|------|------------|---------|--------|--------------|--------------------|----------------|--------------|
| ten8t_checker.py   | 0.47 | 6.50       | 9149.36 | 508.30 | F            | A                  | D              | F            |
| ten8t_function.py  | 0.18 | 6.68       | 3660.46 | 203.36 | C            | A                  | C              | D            |
| ten8t_yield.py     | 0.17 | 4.67       | 2420.79 | 134.49 | C            | A                  | C              | C            |
| ten8t_util.py      | 0.10 | 3.80       | 1119.81 | 62.21  | B            | A                  | B              | B            |
| ten8t_attribute.py | 0.08 | 6.00       | 1483.05 | 82.39  | B            | A                  | B              | B            |
| ten8t_module.py    | 0.06 | 5.36       | 1025.19 | 56.95  | B            | A                  | B              | B            |
| ten8t_ruid.py      | 0.03 | 3.75       | 378.84  | 21.05  | A            | A                  | A              | A            |
| ten8t_result.py    | 0.03 | 2.71       | 232.47  | 12.92  | A            | A                  | A              | A            |
| ten8t_filter.py    | 0.03 | 2.00       | 159.45  | 8.86   | A            | A                  | A              | A            |
| ten8t_package.py   | 0.03 | 1.64       | 124.60  | 6.92   | A            | A                  | A              | A            |
| ten8t_thread.py    | 0.01 | 1.00       | 15.51   | 0.86   | A            | A                  | A              | A            |
| ten8t_logging.py   | 0.00 | 0.50       | 1.00    | 0.06   | A            | A                  | A              | A            |
| ten8t_exception.py | 0.00 | 0.00       | 0.00    | 0.00   | A            | A                  | A              | A            |
| ten8t_immutable.py | 0.00 | 0.00       | 0.00    | 0.00   | A            | A                  | A              | A            |

<small>radon_hal.csv &nbsp;&nbsp; 17:02:04 2025-03-30</small>

<!--file end-->

__Maintainability Index__
<!--file snippets/radon_mi.csv-->

| File               | Maint.<br>Index | Rank |
|--------------------|-----------------|------|
| ten8t_checker.py   | 27.30           | A    |
| ten8t_yield.py     | 47.50           | A    |
| ten8t_function.py  | 51.80           | A    |
| ten8t_attribute.py | 58.40           | A    |
| ten8t_module.py    | 62.80           | A    |
| ten8t_thread.py    | 63.90           | A    |
| ten8t_result.py    | 64.30           | A    |
| ten8t_util.py      | 64.70           | A    |
| ten8t_filter.py    | 68.20           | A    |
| ten8t_package.py   | 71.70           | A    |
| ten8t_ruid.py      | 78.20           | A    |
| ten8t_logging.py   | 89.50           | A    |
| ten8t_exception.py | 100.00          | A    |
| ten8t_immutable.py | 100.00          | A    |

<small>radon_mi.csv &nbsp;&nbsp; 17:02:04 2025-03-30</small>

<!--file end-->

__Complexity__
NOTE: This is by class. There is some function based code that is invisible (e.g., decorators in `ten8t_attribute.py`).
<!--file snippets/radon_cc.csv-->

| File               | Name                  | Rank | Complexity |
|--------------------|-----------------------|------|------------|
| ten8t_function.py  | Ten8tFunction         | B    | 7.00       |
| ten8t_checker.py   | Ten8tChecker          | A    | 5.00       |
| ten8t_yield.py     | Ten8tYield            | A    | 5.00       |
| ten8t_module.py    | Ten8tModule           | A    | 4.00       |
| ten8t_package.py   | Ten8tPackage          | A    | 3.00       |
| ten8t_result.py    | Ten8tResult           | A    | 3.00       |
| ten8t_thread.py    | Ten8tThread           | A    | 3.00       |
| ten8t_immutable.py | Ten8tEnvList          | A    | 2.00       |
| ten8t_immutable.py | Ten8tEnvDict          | A    | 2.00       |
| ten8t_util.py      | NextIntValue          | A    | 2.00       |
| ten8t_yield.py     | Ten8tYieldPassOnly    | A    | 2.00       |
| ten8t_yield.py     | Ten8tYieldFailOnly    | A    | 2.00       |
| ten8t_yield.py     | Ten8tYieldPassFail    | A    | 2.00       |
| ten8t_yield.py     | Ten8tYieldAll         | A    | 2.00       |
| ten8t_yield.py     | Ten8tYieldSummaryOnly | A    | 2.00       |
| ten8t_exception.py | Ten8tTypeError        | A    | 1.00       |
| ten8t_exception.py | Ten8tValueError       | A    | 1.00       |
| ten8t_exception.py | Ten8tException        | A    | 1.00       |
| ten8t_immutable.py | Ten8tEnvSet           | A    | 1.00       |
| ten8t_yield.py     | Ten8tNoResultSummary  | A    | 1.00       |

<small>radon_cc.csv &nbsp;&nbsp; 17:02:04 2025-03-30</small>

<!--file end-->

## WTH does `Ten8t` and what's with your wierd names?

`Ten8t` is a [numeronym](https://en.wikipedia.org/wiki/Numeronym) for the word 1080 (ten-eighty). I chose this
name after discovering that my initial choices were too similar to existing packages on PyPI.
The name refers to skiing or snowboarding tricks involving 3 rotations.

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

## Contributors

<!--file snippets/contribs.md-->

| Username     | Commits | Last<br>Contribution |
|--------------|--------:|:--------------------:|
| **hucker**   |     124 |      2025-03-29      |
| _dependabot_ |       2 |         N/A          |

<small>contribs.md &nbsp;&nbsp; 17:02:03 2025-03-30</small>

<!--file end-->

## TODO

1. Fix qc scripts to include metrics for code in subpackages.
2. Improve ten8t_checker.py and ten8t_function.py to reduce their complexity numbers.
2. Add support for handling coroutines and async generators, so ten8t can support all function types.
3. Progress bars for using multithreading is broken.
4. Improved decorators so attribute didn't do ALL the work.

## Latest changes

1. Improved the decorator mechanism for setting up check functions.
2. Added a textual demo.
3. Added explicit error messages for async check functions
4. Added support for csv/markdown/excel output from the checker.
