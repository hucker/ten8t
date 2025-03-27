"""
The yield class is used to track yield of TR result objects so pass/fail and summary
statistics can easily be provided by users of the class.  Many rule functions uses
yield objects to reliably track state.
"""
from enum import Enum
from functools import wraps
from typing import Generator

from .ten8t_exception import Ten8tException
from .ten8t_result import Ten8tResult


class Ten8tNoResultSummary(Enum):
    """
    Controls how having NO results impacts summaries creating summaries.

    """
    SummaryPassOnNone = "SummaryPassOnNone"  # Emit a passing summary that says "no results"
    SummaryFailOnNone = "SummaryFailOnNone"  # Emit a failing summary that says "no results"

    # Note these two cases elevate a summary result to a regular result.  This is nice because it
    # can make it so you always have atlease one record for every test.
    ResultFailOnNone = "ResultFailOnNone"  # Emit a failing RESULT if there are no results
    ResultPassOnNone = "ResultPassOnNone"  # Emit a passing RESULT if there are no results

    SkipOnNone = "SkipOnNone"  # If there is nothing then skip it!


DEFAULT_NO_RESULT = Ten8tNoResultSummary.SummaryPassOnNone


# For now we default to reporting a passing summary record if they ask for one and there is no data.


class Ten8tYield:
    """
    This object allows you to write code that looks like it is yielding
    all passes, fails, exceptions and summary results. The code looks
    like it is yielding as it goes.  What happens under the covers is
    the object looks at its configuration and only yields what it was
    told to yield, and it tracks a summary.  The benefit of this is that
    all code ONLY looks like the sunny day case and not top level
    code is ever required to do all the checks and accounting.  This
    allows all rules that process lists of "stuff" to work the same
    way with clean code.

    Check functions may be called to handle
    many things rather than one thing.  Are all the files in this
    folder smaller than 1kb, are all the modification times < 1hr
    old. These situations raise the need to have counts, to
    track pass/fail and to have (possibly only) summary messages.
    There is a lot of messing around to track this "stuff".

    This class allows you to create a yield object that
    tracks every time you have yielded while tracking pass
    fail counts.  You can have summary_only set to true so
    that the intermediate results are not yielded allowing you
    to have a single result rather than one for each constituent.

    This class is tightly coupled to the Ten8tResult class because
    I want it to look like a result (because that is what is passed
    every time it is used)

    These internal counts allow top level code to NOT manage that
    state at the rule level.  Instead, you just report your passes

    and fails and ask at the end how it played out.

    y = Ten8tYield()

    if cond:
        yield from y(TR(True,"Info...")
    if not y.yielded:
        yield from y(TR(False,"Nothing to do"))
    if emit_summary:
        yield TR(status=self.fail_count==0,msg=f"{self.pass_count} passes "
                 f"and {self.fail_count} fails")

    """

    def __init__(self, *,
                 emit_pass: bool = True,
                 emit_fail: bool = True,
                 emit_summary: bool = False,
                 summary_name: str = "",
                 no_results: Ten8tNoResultSummary = DEFAULT_NO_RESULT):
        """
        The ten8t yield class allows you to use the yield mechanism while also tracking
        pass fail status of the generator.  Using this class allows for a separation of
        concerns so your top level code doesn't end up tracking ALOT of state information
        for every check that is performed.

        When your test is complete you can query the yield object and report the
        statistics with minimal overhead.

        If you set emit_summary to true you will get a summary result that can be
        very useful in the case that

        If you provide a name to this init then a generic summary message can be
        generated like this:

        y = Ten8tYield(summary_name="Generic Test",emit_summary=True)
        y(status=True,msg="Test1")
        y(status=True,msg="Test2")
        y(status=False,msg="Test3")
        y.emit_summary()

        TR(status=False,msg="Generic Test had 2 pass and 1 fail results for 66.7%.")

        y = Ten8tYield(summary_name="Generic Test",emit_summary=False)
        y(status=True,msg="Test1")
        y(status=True,msg="Test2")
        y(status=False,msg="Test3")
        y.emit_summary()

        TR(status=True,msg="Generic Test")
        TR(status=True,msg="Generic Test")
        TR(status=False,msg="Generic Test")

        Note: All arguments MUST be passed as keyword arguments.

        Args:
            emit_pass(bool): Yield pass results. Defaults to True
            emit_fail(bool): Yield fail results. Defaults to True
            emit_summary(bool): Show summary message. Defaults to False
            summary_name: Defaults to ""
        """
        self._count = 0
        self.emit_pass = emit_pass
        self.emit_fail = emit_fail
        self._fail_count = 0
        self.emit_summary = emit_summary
        self.summary_name = summary_name
        self.original_func_name = ''
        self.no_results = no_results

        if not any([emit_pass, emit_fail, emit_summary]):
            raise Ten8tException("You must show a result or a summary.")

    @property
    def yielded(self) -> bool:
        """ Have we yielded once?"""
        return self._count > 0

    @property
    def count(self) -> int:
        """How many times have we yielded?"""
        return self._count

    @property
    def fail_count(self) -> int:
        """How many fails have there been"""
        return self._fail_count

    @property
    def pass_count(self) -> int:
        """How many passes have there been"""
        return self.count - self._fail_count

    @property
    def counts(self) -> tuple[int, int, int]:
        """Return pass/fail/total yield counts"""
        return self.pass_count, self.fail_count, self.count

    def increment_counter(self, result: Ten8tResult) -> int:
        """Increment counters based on result status."""
        self._count += 1
        if not result.status:
            self._fail_count += 1

        # This is a bit of a hack.  In cases where we make a summary message, and the
        # user is mean and doesn't give us one, it would be nice to give them a clue
        # of where this came from
        if not self.original_func_name:
            self.original_func_name = result.func_name

        return self._count

    def results(self,
                results: Ten8tResult | list[Ten8tResult]) -> Generator[Ten8tResult, None, None]:
        """
        This lets you pass a result or results to be yielded and mimics the way ten8t results
        work in other places where traditional result collection is used, for example code
        that returns a list of Ten8tResults
        Args:
            results: one or list of ten8t results
        Returns:

        """
        if isinstance(results, Ten8tResult):
            results = [results]

        if isinstance(results, Generator) or (isinstance(results, list) and
                                              isinstance(results[0], Ten8tResult)):
            # At this point we are iterating over a list or a generator.
            for result in results:
                if isinstance(result, Ten8tResult):
                    self.increment_counter(result)
                    if self.emit_pass and result.status or self.emit_fail and not result.status:
                        yield result
                else:
                    raise Ten8tException(f"Unknown result type {type(results)}")
        else:
            raise Ten8tException(f"Unknown result type {type(results)}")

    def __call__(self, *args_, **kwargs_) -> Generator[Ten8tResult, None, None]:
        """
        Syntactic sugar to make yielding look just like creating the TR object at each
        invocation of yield.  The code mimics creating a Ten8tResult manually
        since the *args/**kwargs are passed through via a functools.wrapper.

        Please note that this really tries to play along with what people might (reasonably?)
        try to do, so if they pass in a list of results, the code will just yield them
        away.


        y.results(BR(status=True,msg="Did it work?"))

        The __call_ override allows the following code to work correctly without having to manually
        instantiate a Ten8tResult.

        y(status=True,msg="Did it work?")

        Under the covers all the parameters to this function are forward to the creation of
        the underlying Ten8tResult inside the wrapper.


        Args:
            *args_: For Ten8tResult
            **kwargs_: For Ten8tResult
        """

        @wraps(Ten8tResult.__init__)
        def tr_wrapper(*args, **kwargs):
            """
            Make the __call__ method have the same parameter list as the Ten8tResult.__init__
            method.

            You can say:
            y(status=True,msg="Did it work?")

            or you can do

            y(TR(status=True,msg="Did it work?")

            Args:
                *args:   Handle any function args
                **kwargs: Handle any function kwargs

            Returns:

            """
            return Ten8tResult(*args, **kwargs)

        # If they just hand you a result then just pass it on
        if len(args_) == 1 and len(kwargs_) == 0 and isinstance(args_[0], Ten8tResult):
            results: list[Ten8tResult] = [args_[0]]

        # This is when we get a generator
        elif len(args_) == 1 and len(kwargs_) == 0 and isinstance(args_[0], Generator):
            results: list[Ten8tResult] = list(args_[0])
        else:
            # THIS branch of the if is what we should do 99% of the time since this has all
            # the syntactic sugar to make yielding a result similar to constructing a TR.
            # tr_wrapper is made with the @wraps so it looks just like a Ten8t initializer's
            # args and kwargs and passes them into the Ten8tResult initializer.
            results = [tr_wrapper(*args_, **kwargs_)]
        for result in results:

            self.increment_counter(result)
            if (self.emit_fail and not result.status) or (self.emit_pass and result.status):
                yield result

    def yield_summary(self, name="", msg="") -> Generator[Ten8tResult, None, None]:
        """
        The yield summary should be the name of the summary followed information message
        about the summary.  The message should give a pass and fail count.  If no name
        or message is provided the function name is used and a generic message is
        created. Generally the name should be provided since the function name is only
        good enough for very simple cases.  In general the message is good enough since
        it is nice to have all summaries look the same with the pass and fail count.

        Since this is yielding a summary the summary_result flag is set to enable filtering.

        Please note that the call looks like where you yield from

        yield from y.emit_summary()

        Args:
            name: Provide a name for the yield summary to override the one at init time.
            msg: Provide a completely custom message

        Returns:

        """
        if self.emit_summary:
            name = name or self.summary_name or self.original_func_name
            msg = msg or f"{name} had {self.pass_count} pass and {self.fail_count} fail."

            if self.yielded:
                yield Ten8tResult(status=self.fail_count == 0, msg=msg, summary_result=True)
            else:

                # This handles all the ways you might want to handle summary results
                # when there are no results.
                if self.no_results.name == Ten8tNoResultSummary.SummaryFailOnNone.name:
                    yield Ten8tResult(status=False, msg=msg, summary_result=True)
                elif self.no_results.name == Ten8tNoResultSummary.SummaryPassOnNone.name:
                    yield Ten8tResult(status=True, msg=msg, summary_result=True)
                elif self.no_results.name == Ten8tNoResultSummary.ResultPassOnNone.name:
                    yield Ten8tResult(status=True, msg=msg, summary_result=False)
                elif self.no_results.name == Ten8tNoResultSummary.ResultFailOnNone.name:
                    yield Ten8tResult(status=False, msg=msg, summary_result=False)
                elif self.no_results.name == Ten8tNoResultSummary.SkipOnNone.name:
                    yield Ten8tResult(status=None, msg=msg, skipped=True)
                else:
                    raise Ten8tException("Unknown no_results value %s", self.no_results)


# These are useful subclasses that may be passed as the yield object inside of rule functions.


class Ten8tYieldPassOnly(Ten8tYield):
    """ Only yield pass results from a rule function."""

    def __init__(self, summary_name: str = "Yield Pass Results"):
        super().__init__(emit_summary=False, emit_pass=True, emit_fail=False, summary_name=summary_name)


class Ten8tYieldFailOnly(Ten8tYield):
    """ Only yield fail results from a rule function."""

    def __init__(self, summary_name: str = "Yield Fail Results"):
        super().__init__(emit_summary=False, emit_pass=False, emit_fail=True, summary_name=summary_name)


class Ten8tYieldPassFail(Ten8tYield):
    """ Only yield pass and fail results from a rule function."""

    def __init__(self, summary_name: str = "Yield Pass/Fail Results"):
        super().__init__(emit_summary=False, emit_pass=True, emit_fail=True, summary_name=summary_name)


class Ten8tYieldAll(Ten8tYield):
    """ Yield everything. """

    def __init__(self, summary_name: str = "Yield All Results"):
        super().__init__(emit_summary=True, emit_pass=True, emit_fail=True, summary_name=summary_name)


class Ten8tYieldSummaryOnly(Ten8tYield):
    """
    Only yield summary results from a rule function.

    This case could be considered swapping out the pass/fail machinery for the summary thus
    making the summary an actual test...and no longer being the summary since it is the only record
    of the test.  For now, I'll leave this, but I think this case should have the lower level
    yield object detect that both pass/fails are turned off.
    """

    def __init__(self, summary_name: str = ""):
        super().__init__(emit_summary=True, emit_pass=False, emit_fail=False, summary_name=summary_name)
