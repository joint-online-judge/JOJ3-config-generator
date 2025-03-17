from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, ClassVar, Dict, List

import inquirer
from pydantic import BaseModel, ConfigDict


class LanguageInterface(ABC):
    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    class Stage(str, Enum): ...

    @abstractmethod
    class Attribute(BaseModel): ...

    stages: ClassVar[List[Enum]]
    attribute: ClassVar[BaseModel]

    @classmethod
    def set_stages(cls, stages: List[str]) -> None:
        cls.stages = [cls.Stage(stage) for stage in stages]

    @classmethod
    def set_attribute(cls, attribute_dict: Dict[str, Any]) -> None:
        cls.attribute = cls.Attribute(**attribute_dict)

    @classmethod
    @abstractmethod
    def get_attribute_questions(cls) -> List[Any]: ...


class Cpp(LanguageInterface):
    def __str__(self) -> str:
        return "C++"

    class Stage(str, Enum):
        COMPILATION = "Compilation"
        CPPCHECK = "Cppcheck"
        CPPLINT = "Cpplint"
        CLANG_TIDY = "Clang-Tidy"
        RUN = "Run"

    class Attribute(BaseModel):
        compile_command: str = "make"
        run_command: str = "./a.out"

    stages = []
    attribute = Attribute()

    @classmethod
    def get_attribute_questions(cls) -> List[Any]:
        return [
            inquirer.Text(
                name="compile_command",
                message="Compile command",
                default=cls.attribute.compile_command,
            ),
            inquirer.Text(
                name="run_command",
                message="Run command",
                default=cls.attribute.run_command,
            ),
        ]


class Python(LanguageInterface):
    def __str__(self) -> str:
        return "Python"

    class Stage(str, Enum):
        RUN = "Run"

    class Attribute(BaseModel):
        run_command: str = "python3 main.py"

    stages = []
    attribute = Attribute()

    @classmethod
    def get_attribute_questions(cls) -> List[Any]:
        return [
            inquirer.Text(
                name="run_command",
                message="Run command",
                default=cls.attribute.run_command,
            ),
        ]


class Rust(LanguageInterface):
    def __str__(self) -> str:
        return "Rust"

    class Stage(str, Enum):
        COMPILATION = "Compilation"
        CLIPPY = "Clippy"
        RUN = "Run"

    class Attribute(BaseModel):
        pass

    stages = []
    attribute = Attribute()

    @classmethod
    def get_attribute_questions(cls) -> List[Any]:
        return []


LANGUAGES = [
    Cpp(),
    Python(),
    Rust(),
]


class Answers(BaseModel):
    name: str
    language: LanguageInterface

    model_config = ConfigDict(arbitrary_types_allowed=True)
