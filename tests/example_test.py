# from xxx import generate


from typing import Any

import pytest


@pytest.mark.xfail(strict=True)
def test_generate() -> None:
    generate = lambda x: x  # TODO: real generate function imported
    data_input: dict[Any, Any] = {}  # TODO: load real input from some file
    data_output: dict[Any, Any] = generate(data_input)
    expected_output: dict[Any, Any] = {
        "a": "b"
    }  # TODO: load real output from some file
    assert data_output == expected_output
