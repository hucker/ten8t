from functools import wraps
from typing import Generator

from .ten8t_exception import Ten8tException
from .ten8t_result import Ten8tResult


class Ten8tYield:
    """
    This allows syntactic sugar to know how many times a generator
    has been fired and how many passes and fails have occurred.

    These internal counts allow top level code to NOT manage that
    state at the rule level.  Instead, you just report your passes

    and fails and ask at the end how it played out.

    gen = BrickYield()

    if cond:
        yield from gen(BR(True,"Info...")
    if not gen.yielded:
        yield from gen(BR(False,"Nothing to do"))
    if show_summary:
        yield BR(status=self.fail_count==0,msg=f"{self.pass_count} passes "
                 f"and {self.fail_count} fails")

    """

    def __init__(self, summary_only=False, summary_name=""):
        """
        The ten8t yield class allows you to use the yield mechanism while also tracking
        pass fail status of the generator.  Using this class allows for a separation of
        concerns so your top level code doesn't end up counting passes and fails.

        When your test is complete you can query the yield object and report that
        statistics without a bunch of overhead.

        If you set summary_only to true, no messages will be yielded, but you
        can yield the summary message manually when you are done with the test.

        If you provide a name to this init then a generic summary message can be
        generated like this:

        y = Ten8tYield("Generic Test")
        y(status=True,msg="Test1")
        y(status=True,msg="Test2")
        y(status=False,msg="Test3")
        y.yield_summary()

        BR(status=False,msg="Generic Test had 2 pass and 1 fail results for 66.7%.")

        Args:
            summary_only(bool): Defaults to False
            summary_name: Defaults to ""
        """
        self._count = 0
        self._fail_count = 0
        self.summary_only = summary_only
        self.summary_name = summary_name

    @property
    def yielded(self):
        """ Have we yielded once?"""
        return self._count > 0

    @property
    def count(self):
        """How many times have we yielded?"""
        return self._count

    @property
    def fail_count(self):
        """How many fails have there been"""
        return self._fail_count

    @property
    def pass_count(self):
        """How many passes have there been"""
        return self.count - self._fail_count

    @property
    def counts(self):
        """Return pass/fail/total yield counts"""
        return self.pass_count, self.fail_count, self.count

    def increment_counter(self, result: Ten8tResult) -> None:
        """Increment counters based on result status."""
        self._count += 1
        if not result.status:
            self._fail_count += 1

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
                    if not self.summary_only:
                        yield result
                else:
                    raise Ten8tException(f"Unknown result type {type(results)}")
        else:
            raise Ten8tException(f"Unknown result type {type(results)}")

    def __call__(self, *args_, **kwargs_) -> Generator[Ten8tResult, None, None]:
        """
        Syntactic sugar to make yielding look just like creating the BR object at each
        invocation of yield.  The code mimics creating a Ten8tResult manually
        since the *args/**kwargs are passed through via a functools.wrapper.

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
        def sr_wrapper(*args, **kwargs):
            """
            Make the __call__ method have the same parameter list as the Ten8tResult.__init__
            method.

            You can say:
            y(status=True,msg="Did it work?")

            or you can do

            y(BR(status=True,msg="Did it work?")

            Args:
                *args:   Handle any function args
                **kwargs: Handle any function kwargs

            Returns:

            """
            return Ten8tResult(*args, **kwargs)

        # If they just hand you a result then just pass it on
        if len(args_) == 1 and len(kwargs_) == 0 and isinstance(args_[0], Ten8tResult):
            results = [args_[0]]

        # This is when we get a generator
        elif len(args_) == 1 and len(kwargs_) == 0 and isinstance(args_[0], Generator):
            results = [x for x in args_[0]]
        else:
            # package up the result information
            results = [sr_wrapper(*args_, **kwargs_)]
        for result in results:
            self.increment_counter(result)
            if not self.summary_only:
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
        Args:
            name:
            msg:

        Returns:

        """
        name = name or self.summary_name or self.__call__.__name__
        msg = msg or f"{name} had {self.pass_count} pass and {self.fail_count} fail."

        yield Ten8tResult(status=self.fail_count == 0, msg=msg, summary_result=True)
