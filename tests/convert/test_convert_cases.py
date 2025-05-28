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


def test_keyword() -> None:
    load_case("keyword")


def test_result_detail() -> None:
    load_case("result-detail")


def test_elf() -> None:
    load_case("elf")
