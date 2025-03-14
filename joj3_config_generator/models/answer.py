from enum import Enum
from typing import List

from pydantic import AliasChoices, BaseModel, Field


class StageEnum(str, Enum):
    COMPILATION = "Compilation"
    CPPCHECK = "Cppcheck"
    CPPLINT = "Cpplint"
    CLANG_TIDY = "Clang-Tidy"


class Answers(BaseModel):
    name: str
    type_: str = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type_", "type"),
    )
    stages: List[str]
