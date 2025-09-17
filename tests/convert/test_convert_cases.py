import pytest
from pydantic import ValidationError

from tests.convert.utils import load_case


def test_basic() -> None:
    load_case("basic")


def test_clang_tidy() -> None:
    load_case("clang-tidy")


def test_cppcheck() -> None:
    load_case("cppcheck")


def test_cpplint() -> None:
    load_case("cpplint")


def test_diff() -> None:
    load_case("diff")


def test_elf() -> None:
    load_case("elf")


def test_empty() -> None:
    load_case("empty")


def test_extra_field() -> None:
    with pytest.raises(ValidationError):
        load_case("extra-field")


def test_full() -> None:
    load_case("full")


def test_keyword() -> None:
    load_case("keyword")


def test_result_detail() -> None:
    load_case("result-detail")


def test_unnecessary() -> None:
    load_case("unnecessary")
