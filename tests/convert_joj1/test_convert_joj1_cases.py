import pytest

from tests.convert_joj1.utils import load_case


@pytest.mark.xfail
def test_basic() -> None:
    load_case("basic")
