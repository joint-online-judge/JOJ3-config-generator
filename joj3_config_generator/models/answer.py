from enum import Enum
from typing import List

from pydantic import BaseModel


class StageEnum(str, Enum):
    COMPILATION = "Compilation"
    CPPCHECK = "Cppcheck"
    CPPLINT = "Cpplint"
    CLANG_TIDY = "Clang-Tidy"


class Answers(BaseModel):
    name: str
    stages: List[str]
