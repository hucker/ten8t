#!/user/bin/env -S uv run --script
# /// script
# dependencies = ["ten8t>=0.0.22"]
# ///

import pathlib

import ten8t as t8
from ten8t import Ten8tBasicMarkdownRenderer, Ten8tChecker


@t8.categories(tag="file")
def check_rule1():
    root = pathlib.Path('./examples/file_system')
    for folder in [root / f for f in ['folder1', 'folder2', 'folder3']]:
        yield from t8.rule_large_files(folders=folder, pattern="*.txt", max_size=100_000)


@t8.categories(tag="tag")
def check_rule2(cfg):  # <-- Config file has the test setup
    """cfg: application config file."""
    for folder in cfg['logging']['folders']:
        yield from t8.rule_stale_files(folders=folder, pattern="*.txt", minutes=5.0)


cfg = {'cfg': {'logging': {'folders': ["../examples/file_system/folder1"]}}}

ch: Ten8tChecker = t8.Ten8tChecker(check_functions=[check_rule1, check_rule2],
                                   env=cfg,
                                   renderer=Ten8tBasicMarkdownRenderer())

for r in ch.yield_all():
    print(ch.result_strategy.render(r))
print(ch.status_strategy.render(ch))
