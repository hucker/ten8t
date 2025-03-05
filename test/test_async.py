import pytest

import ten8t as t8


def test_no_async_generators():
    async def check_async_gen():  # pragma no cover
        async for x in [1, 2, 3]:
            yield x

    with pytest.raises(t8.Ten8tException) as e_info:
        _ = t8.Ten8tFunction(check_async_gen)
    assert "not YET supported" in str(e_info)


def test_no_coroutines():
    async def check_no_coroutine():  # pragma no cover
        return 1

    with pytest.raises(t8.Ten8tException) as e_info:
        _ = t8.Ten8tFunction(check_no_coroutine)
    assert "not YET supported" in str(e_info)
