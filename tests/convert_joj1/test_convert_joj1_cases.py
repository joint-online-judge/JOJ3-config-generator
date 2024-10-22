import pytest

from joj3_config_generator.convert import convert_joj1
from tests.convert_joj1.utils import read_convert_joj1_files


@pytest.mark.xfail
def test_basic() -> None:
    joj1, expected_result = read_convert_joj1_files("basic")
    result = convert_joj1(joj1).model_dump(by_alias=True)
    assert result == expected_result
