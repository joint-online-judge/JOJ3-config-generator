from typing import List, Optional

from pydantic import BaseModel, Field


class Language(BaseModel):
    language: str
    type: Optional[str] = None
    compiler_file: Optional[str] = None
    compiler_args: Optional[str] = None
    code_file: Optional[str] = None
    execute_file: Optional[str] = None
    execute_args: Optional[str] = None


class Case(BaseModel):
    time: str = Field(default="1s")
    memory: str = Field(default="32m")
    score: int = Field(default=10)
    input: str
    output: str
    execute_args: Optional[str] = None
    category: Optional[str] = None


class Config(BaseModel):
    languages: List[Language]
    cases: List[Case]
