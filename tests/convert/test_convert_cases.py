from joj3_config_generator.convert import convert
from tests.convert.utils import read_convert_files


def test_basic() -> None:
    repo, task, expected_result = read_convert_files("basic")
    result = convert(repo, task).model_dump(by_alias=True)
    assert result == expected_result
