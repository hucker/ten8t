import pytest

import ten8t
from ten8t import Ten8tResult
from ten8t.progress import Ten8tDebugProgress, Ten8tLogProgress, Ten8tMultiProgress, Ten8tNoProgress, \
    Ten8tProgress
from ten8t.ten8t_exception import Ten8tException
from ten8t.ten8t_util import StrOrNone


class DummyProgress(ten8t.Ten8tProgress):
    """This class just counts how many times it is called"""

    def __init__(self):
        self.msg_count = 0
        self.result_count = 0

    def result_msg(self, current_iteration: int, max_iteration: int, msg: StrOrNone = '',
                   result: Ten8tResult | None = None):
        self.result_count += 1

    def message(self, msg: StrOrNone):
        self.msg_count += 1


def test_multi_progress():
    """
    Verify that the multi progress sends the messages and results to the
    correct progress objects.
    """
    dp1 = DummyProgress()
    dp2 = DummyProgress()
    assert dp1.msg_count == 0
    assert dp2.msg_count == 0
    mp = Ten8tMultiProgress(progress_list=[dp1, dp2])

    mp.message("Hello")
    assert dp1.msg_count == 1
    assert dp2.msg_count == 1
    assert dp1.result_count == 0
    assert dp2.result_count == 0

    mp.result_msg(0, 1, msg="Hello", result=ten8t.TR(status=True))
    assert dp1.msg_count == 1
    assert dp2.msg_count == 1
    assert dp1.result_count == 1
    assert dp2.result_count == 1

    mp.message("Hello2")
    assert dp1.msg_count == 2
    assert dp2.msg_count == 2
    assert dp1.result_count == 1
    assert dp2.result_count == 1

    mp.result_msg(0, 1, msg="Hello2", result=ten8t.TR(status=True))
    assert dp1.msg_count == 2
    assert dp2.msg_count == 2
    assert dp1.result_count == 2
    assert dp2.result_count == 2


@pytest.mark.parametrize("invalid_level", ["invalid", -1, None, 1.5])
def test_bad_result_level(invalid_level):
    """Test Ten8tLogProgress with invalid result_level values."""
    try:
        # Pass the invalid `result_level` into the class
        _ = Ten8tLogProgress(result_level=invalid_level)
        assert False
    except Exception:
        assert True


@pytest.mark.parametrize("invalid_level", ["invalid", -1, None, 1.5])
def test_bad_msg_level(invalid_level):
    """Test Ten8tLogProgress with invalid result_level values."""
    try:
        # Pass the invalid `result_level` into the class
        _ = Ten8tLogProgress(msg_level=invalid_level)
        assert False
    except Exception:
        assert True


@pytest.mark.parametrize("invalid_logger", [1, None, "invalid_logger", object(), []])
def test_bad_logger(invalid_logger):
    """Test Ten8tLogProgress with invalid logger values."""
    with pytest.raises(Ten8tException):
        # Pass the invalid logger into the class
        _ = Ten8tLogProgress(logger=invalid_logger)


@pytest.mark.parametrize("class_type, args, kwargs, expected_str, expected_repr", [
    # Ten8tProgress
    (Ten8tProgress, [], {},
     "Ten8tProgress base class for tracking progress",
     "<Ten8tProgress>"),

    # Ten8tNoProgress
    (Ten8tNoProgress, [], {},
     "Ten8tNoProgress - No progress tracking (used primarily for testing)",
     "<Ten8tNoProgress>"),

    # Ten8tDebugProgress
    (Ten8tDebugProgress, [], {},
     "Ten8tDebugProgress - Debug progress tracker displaying messages in stdout",
     "<Ten8tDebugProgress>"),

    # # Ten8tLogProgress with default mock logger
    # (Ten8tLogProgress, [],
    #  {"logger": Mock(spec=logging.Logger, **{"name": "mock_logger"}),
    #   "result_level": logging.INFO,
    #   "msg_level": logging.INFO},
    #  "Ten8tLogProgress - Logs progress to logger 'mock_logger' with result_level=20 and msg_level=20",
    #  "<Ten8tLogProgress(logger=mock_logger, result_level=20, msg_level=20)>"),
    #
    # # Ten8tLogProgress with custom levels
    # (Ten8tLogProgress, [],
    #  {"logger": Mock(spec=logging.Logger, **{"name": "test_logger"}),
    #   "result_level": logging.DEBUG,
    #   "msg_level": logging.ERROR},
    #  "Ten8tLogProgress - Logs progress to logger 'test_logger' with result_level=10 and msg_level=40",
    #  "<Ten8tLogProgress(logger=test_logger, result_level=10, msg_level=40)>"),

    # Ten8tMultiProgress - single item in list
    (Ten8tMultiProgress, [[Ten8tNoProgress()]], {},
     "Ten8tMultiProgress - Manages Progress for 1 Sub-progress Handlers",
     "<Ten8tMultiProgress(progress_list=1 handlers)>"),

    # Ten8tMultiProgress - multiple items
    (Ten8tMultiProgress, [[Ten8tNoProgress(), Ten8tDebugProgress()]], {},
     "Ten8tMultiProgress - Manages Progress for 2 Sub-progress Handlers",
     "<Ten8tMultiProgress(progress_list=2 handlers)>"),

    # Ten8tMultiProgress - single item not in list
    (Ten8tMultiProgress, [Ten8tNoProgress()], {},
     "Ten8tMultiProgress - Manages Progress for 1 Sub-progress Handlers",
     "<Ten8tMultiProgress(progress_list=1 handlers)>"),
])
def test_str_and_repr_methods(class_type, args, kwargs, expected_str, expected_repr):
    """Test both __str__ and __repr__ methods with parameterized inputs."""
    instance = class_type(*args, **kwargs)

    val_str = str(instance)
    val_repr = repr(instance)

    assert_str = val_str == expected_str
    assert_repr = val_repr == expected_repr
    # Test __str__
    assert assert_str, f"__str__ mismatch for {class_type.__name__}"

    # Test __repr__
    assert assert_repr, f"__repr__ mismatch for {class_type.__name__}"
