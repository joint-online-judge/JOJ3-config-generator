from abc import ABC, abstractmethod
from enum import Enum
from importlib import resources
from typing import Any, ClassVar, Dict, List, Type

import inquirer
from pydantic import BaseModel, ConfigDict


class LanguageInterface(ABC):
    name: ClassVar[str]

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

    @classmethod
    def get_template_questions(cls) -> List[Any]:
        anchor = "joj3_config_generator.templates"
        templates_dir = resources.files(anchor).joinpath(cls.name)
        choices = []
        for entry in templates_dir.iterdir():
            if entry.is_file() and entry.name.endswith(".toml"):
                choices.append((entry.name, entry.read_text()))
        return [
            inquirer.List(
                "template_file_content",
                message="Which template file do you want?",
                choices=choices,
            ),
        ]


class Cpp(LanguageInterface):
    name = "C++"

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
        attribute: Cpp.Attribute = cls.attribute
        return [
            inquirer.Text(
                name="compile_command",
                message="Compile command",
                default=attribute.compile_command,
            ),
            inquirer.Text(
                name="run_command",
                message="Run command",
                default=attribute.run_command,
            ),
        ]


class Python(LanguageInterface):
    name = "Python"

    class Stage(str, Enum):
        RUN = "Run"

    class Attribute(BaseModel):
        run_command: str = "python3 main.py"

    stages = []
    attribute = Attribute()

    @classmethod
    def get_attribute_questions(cls) -> List[Any]:
        attribute: Python.Attribute = cls.attribute
        return [
            inquirer.Text(
                name="run_command",
                message="Run command",
                default=attribute.run_command,
            ),
        ]


class Rust(LanguageInterface):
    name = "Rust"

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
        attribute: Rust.Attribute = cls.attribute
        return []


class C(LanguageInterface):
    name = "C"

    class Attribute(BaseModel):
        pass

    stages = []
    attribute = Attribute()

    @classmethod
    def get_attribute_questions(cls) -> List[Any]:
        attribute: C.Attribute = cls.attribute
        return []


class Java(LanguageInterface):
    name = "Java"

    class Attribute(BaseModel):
        pass

    stages = []
    attribute = Attribute()

    @classmethod
    def get_attribute_questions(cls) -> List[Any]:
        attribute: Java.Attribute = cls.attribute
        return []


class Elm(LanguageInterface):
    name = "Elm"

    class Attribute(BaseModel):
        pass

    stages = []
    attribute = Attribute()

    @classmethod
    def get_attribute_questions(cls) -> List[Any]:
        attribute: Elm.Attribute = cls.attribute
        return []


class Matlab(LanguageInterface):
    name = "Matlab"

    class Attribute(BaseModel):
        pass

    stages = []
    attribute = Attribute()

    @classmethod
    def get_attribute_questions(cls) -> List[Any]:
        attribute: Matlab.Attribute = cls.attribute
        return []


class Octave(LanguageInterface):
    name = "Octave"

    class Attribute(BaseModel):
        pass

    stages = []
    attribute = Attribute()

    @classmethod
    def get_attribute_questions(cls) -> List[Any]:
        attribute: Octave.Attribute = cls.attribute
        return []


class JavaScript(LanguageInterface):
    name = "JavaScript"

    class Attribute(BaseModel):
        pass

    stages = []
    attribute = Attribute()

    @classmethod
    def get_attribute_questions(cls) -> List[Any]:
        attribute: JavaScript.Attribute = cls.attribute
        return []


class Go(LanguageInterface):
    name = "Go"

    class Attribute(BaseModel):
        pass

    stages = []
    attribute = Attribute()

    @classmethod
    def get_attribute_questions(cls) -> List[Any]:
        attribute: Go.Attribute = cls.attribute
        return []


LANGUAGES: List[Type[LanguageInterface]] = [
    C,
    Cpp,
    Python,
    Rust,
    Java,
    Elm,
    Matlab,
    Octave,
    JavaScript,
    Go,
]


class Answers(BaseModel):
    name: str
    language: Type[LanguageInterface]
    template_file_content: str = ""

    model_config = ConfigDict(arbitrary_types_allowed=True)
