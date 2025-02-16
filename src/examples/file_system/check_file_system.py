"""Sample ten8t module with check functions"""
from ten8t import attributes, rule_files


@attributes(tag="folder", ruid="f1", level=1, phase="proto")
def check_folder1():
    """ Simple always passing function"""
    yield from rule_files.rule_path_exists('../examples/file_system/folder1')


@attributes(tag="folder", ruid="f2", level=1, phase="proto")
def check_folder2():
    """ Simple always passing function"""
    yield from rule_files.rule_path_exists('../examples/file_system/folder2')


@attributes(tag="folder", ruid="file2", level=1, phase="proto")
def check_files_f2():
    """ Simple always passing function"""
    for f in ['file1.txt', 'file2.txt']:
        yield from rule_files.rule_path_exists(f'../examples/file_system/folder2/{f}')


@attributes(tag="folder", ruid="file1", level=1, phase="proto")
def check_files_f1():
    """ Simple always passing function"""
    for f in ['file1.txt', 'file2.txt']:
        yield from rule_files.rule_path_exists(f'../examples/file_system/folder1/{f}')
