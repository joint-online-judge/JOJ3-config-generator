from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field, field_validator, model_validator

from joj3_config_generator.models.common import Memory, Time
from joj3_config_generator.models.const import (
    DEFAULT_CPU_LIMIT,
    DEFAULT_FILE_LIMIT,
    DEFAULT_MEMORY_LIMIT,
)


class ParserResultDetail(BaseModel):
    time: Optional[bool] = True  # Display run time
    mem: Optional[bool] = True  # Display memory usage
    stdout: Optional[bool] = False  # Display stdout messages
    stderr: Optional[bool] = False  # Display stderr messages
    exitstatus: Optional[bool] = False


class ParserFile(BaseModel):
    name: Optional[str] = None


class ParserLog(BaseModel):
    fileName: Optional[str] = None
    msg: Optional[str] = None
    level: Optional[str] = None


class ParserDummy(BaseModel):
    comment: Optional[str] = ""
    score: Optional[int] = 0
    forcequit: Optional[bool] = False


class ParserKeyword(BaseModel):
    keyword: Optional[List[str]] = []
    weight: Optional[List[int]] = []


class Outputs(BaseModel):
    score: Optional[int] = 0
    ignorespaces: Optional[bool] = True
    hide: Optional[bool] = False
    forcequit: Optional[bool] = False


class ParserDiff(BaseModel):
    output: Optional[Outputs] = Outputs()


class Files(BaseModel):
    import_: Optional[List[str]] = Field([], alias="import")
    export: Optional[List[str]] = []


class Limit(BaseModel):
    mem: int = DEFAULT_MEMORY_LIMIT
    cpu: int = DEFAULT_CPU_LIMIT
    stderr: int = DEFAULT_FILE_LIMIT
    stdout: int = DEFAULT_FILE_LIMIT

    @field_validator("cpu", mode="before")
    @classmethod
    def ensure_time(cls, v: Any) -> Time:
        return Time(v)

    @field_validator("mem", "stdout", "stderr", mode="before")
    @classmethod
    def ensure_mem(cls, v: Any) -> Memory:
        return Memory(v)


class Stage(BaseModel):
    name: Optional[str] = None  # Stage name
    env: Optional[List[str]] = None
    command: Optional[str] = None  # Command to run
    files: Optional[Files] = None
    in_: Optional[str] = Field(None, alias="in")
    out_: Optional[str] = Field(None, alias="out")
    score: Optional[int] = 0
    parsers: Optional[List[str]] = []  # list of parsers
    limit: Limit = Limit()
    dummy: Optional[ParserDummy] = ParserDummy()
    result_status: Optional[ParserDummy] = Field(ParserDummy(), alias="result-status")
    keyword: Optional[ParserKeyword] = ParserKeyword()
    clangtidy: Optional[ParserKeyword] = ParserKeyword()
    cppcheck: Optional[ParserKeyword] = ParserKeyword()
    cpplint: Optional[ParserKeyword] = ParserKeyword()
    result_detail: Optional[ParserResultDetail] = Field(
        ParserResultDetail(), alias="result-detail"
    )
    file: Optional[ParserFile] = ParserFile()
    skip: Optional[List[str]] = []

    # cases related
    cases: Optional[Dict[str, "Stage"]] = None
    diff: Optional[ParserDiff] = ParserDiff()

    model_config = {"extra": "allow"}

    @model_validator(mode="before")
    @classmethod
    def gather_cases(cls: Type["Stage"], values: Dict[str, Any]) -> Dict[str, Any]:
        cases = {k: v for k, v in values.items() if k.startswith("case")}
        for key in cases:
            values.pop(key)
        values["cases"] = {k: v for k, v in cases.items()}
        return values


class Release(BaseModel):
    end_time: Optional[datetime] = None  # RFC 3339 formatted date-time with offset
    begin_time: Optional[datetime] = None


class Task(BaseModel):
    type_: Optional[str] = Field(
        "", serialization_alias="type", validation_alias="type"
    )
    name: str


class Config(BaseModel):
    root: Optional[Path] = None
    path: Optional[Path] = None
    task: Task  # Task name (e.g., hw3 ex5)
    release: Release  # Release configuration
    stages: List[Stage]  # list of stage configurations
