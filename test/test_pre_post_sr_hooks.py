""" Test the pre- and post-hooks for the Ten8tResult"""
import pytest

import ten8t
from src import ten8t as t8


def test_result_pre_hook_result_only():
    """ Test that the pre hook changes the result"""

    @t8.attributes(tag="BoolOnly")
    def hook_test():
        """Hook Test Doc String"""
        yield t8.Ten8tResult(status=True, msg="It works")

    def result_hook1(_, sr):
        sr.status = False
        return sr

    def result_hook2(_, sr):
        sr.msg = "Hooked msg"
        return sr

    sp_func = t8.Ten8tFunction(hook_test, pre_sr_hooks=[result_hook1])
    for result in sp_func():
        assert result.status is False
        assert result.msg == "It works"

    sp_func = t8.Ten8tFunction(hook_test, pre_sr_hooks=[result_hook2])
    for result in sp_func():
        assert result.msg == "Hooked msg"
        assert result.status is True


def test_result_pre_hook_use_class():
    """ Test that the pre hook can use data from the Ten8tFunction class"""

    @t8.attributes(tag="BoolOnly")
    def hook_test():
        """Hook Test Doc String"""
        yield t8.Ten8tResult(status=True, msg="It works")

    def result_doc_string_to_msg(self: t8.Ten8tFunction, sr):
        """ Hook to change the doc string to the msg"""
        sr.msg = self.doc
        return sr

    sp_func = t8.Ten8tFunction(hook_test, pre_sr_hooks=[result_doc_string_to_msg])
    for result in sp_func():
        assert result.msg == "Hook Test Doc String"
        assert result.status is True


def test_verify_post_changes_pre():
    """ Test that the post hook changes the result from the pre hook"""

    @t8.attributes(tag="BoolOnly")
    def hook_test():
        """Hook Test Doc String"""
        yield t8.Ten8tResult(status=True, msg="It works")

    def result_pre(_, sr):
        """ Hard code sr"""
        sr.msg = "Pre Hook"
        sr.status = False
        return sr

    def result_post(_, sr):
        """ Hook to change the doc string to the msg"""
        sr.msg = "Post Hook"
        sr.status = True
        return sr

    sp_func = t8.Ten8tFunction(hook_test, pre_sr_hooks=[result_pre], post_sr_hooks=[result_post])
    for result in sp_func():
        assert result.msg == "Post Hook"
        assert result.status is True


def test_hook_except():
    @t8.attributes(tag="BoolOnly")
    def hook_test():
        """Hook Test Doc String"""
        yield t8.Ten8tResult(status=True, msg="It works")

    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.Ten8tFunction(hook_test, pre_sr_hooks=1)

    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.Ten8tFunction(hook_test, post_sr_hooks=1)
