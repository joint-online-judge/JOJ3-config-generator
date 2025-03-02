from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Type

from pydantic import BaseModel, Field, field_validator, model_validator

from joj3_config_generator.models.common import Memory, Time
from joj3_config_generator.models.const import (
    DEFAULT_CPU_LIMIT,
    DEFAULT_FILE_LIMIT,
    DEFAULT_MEMORY_LIMIT,
)


class ParserResultDetail(BaseModel):
    time: bool = True  # Display run time
    mem: bool = True  # Display memory usage
    stdout: bool = False  # Display stdout messages
    stderr: bool = False  # Display stderr messages
    exitstatus: bool = False


class ParserFile(BaseModel):
    name: str = ""


class ParserLog(BaseModel):
    file_name: str = Field("", alias="fileName")
    msg: str = ""
    level: str = ""


class ParserDummy(BaseModel):
    comment: str = ""
    score: int = 0
    forcequit: bool = False


class ParserKeyword(BaseModel):
    keyword: List[str] = []
    weight: List[int] = []


class Outputs(BaseModel):
    score: int = 0
    ignorespaces: bool = True
    hide: bool = False
    forcequit: bool = False


class ParserDiff(BaseModel):
    output: Outputs = Outputs()


class Files(BaseModel):
    import_: List[str] = Field([], alias="import")
    export: List[str] = []


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
    name: str = ""  # Stage name
    env: List[str] = []
    command: str = ""  # Command to run
    files: Files = Files()
    in_: str = Field("", alias="in")
    out_: str = Field("", alias="out")
    score: int = 0
    parsers: List[str] = []  # list of parsers
    limit: Limit = Limit()
    dummy: ParserDummy = ParserDummy()
    result_status: ParserDummy = Field(ParserDummy(), alias="result-status")
    keyword: ParserKeyword = ParserKeyword()
    clangtidy: ParserKeyword = ParserKeyword()
    cppcheck: ParserKeyword = ParserKeyword()
    cpplint: ParserKeyword = ParserKeyword()
    result_detail: ParserResultDetail = Field(
        ParserResultDetail(), alias="result-detail"
    )
    file: ParserFile = ParserFile()
    skip: List[str] = []

    # cases related
    cases: Dict[str, "Stage"] = {}
    diff: ParserDiff = ParserDiff()

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
    end_time: datetime = datetime.now()  # RFC 3339 formatted date-time with offset
    begin_time: datetime = datetime.now()  # RFC 3339 formatted date-time with offset


class Task(BaseModel):
    type_: str = Field("", serialization_alias="type", validation_alias="type")
    name: str


class Config(BaseModel):
    root: Path = Path(".")
    path: Path = Path("task.toml")
    task: Task  # Task name (e.g., hw3 ex5)
    release: Release  # Release configuration
    stages: List[Stage]  # list of stage configurations
