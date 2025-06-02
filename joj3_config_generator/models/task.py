from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Type

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from joj3_config_generator.models.common import Memory, Time
from joj3_config_generator.models.const import (
    DEFAULT_CASE_SCORE,
    DEFAULT_CPU_LIMIT,
    DEFAULT_FILE_LIMIT,
    DEFAULT_MEMORY_LIMIT,
    DEFAULT_PROC_LIMIT,
)


class ParserResultDetail(BaseModel):
    cpu_time: bool = Field(True, alias="cpu-time")  # Display CPU time
    time: bool = True  # Display run time
    mem: bool = True  # Display memory usage
    stdout: bool = False  # Display stdout messages
    stderr: bool = False  # Display stderr messages
    exit_status: bool = Field(True, alias="exit-status")  # Display exit status
    proc_peak: bool = Field(False, alias="proc-peak")  # Display peak process count
    error: bool = False  # Display error messages


class ParserFile(BaseModel):
    name: str = ""


class ParserLog(BaseModel):
    filename: str
    msg: str = ""
    level: str = ""


class ParserDummy(BaseModel):
    comment: str = ""
    score: int = 0
    force_quit: bool = Field(False, alias="force-quit")


class ParserKeyword(BaseModel):
    keyword: List[str] = []
    weight: List[int] = []


class ParserDiffOutputs(BaseModel):
    score: int = 0
    ignore_spaces: bool = Field(True, alias="ignore-spaces")
    hide: bool = False
    force_quit: bool = Field(False, alias="force-quit")


class ParserDiff(BaseModel):
    output: ParserDiffOutputs = ParserDiffOutputs()
    default_score: int = Field(DEFAULT_CASE_SCORE, alias="default-score")


class StageFiles(BaseModel):
    import_: List[str] = Field([], alias="import")
    export: List[str] = []


class Limit(BaseModel):
    mem: int = DEFAULT_MEMORY_LIMIT
    cpu: int = DEFAULT_CPU_LIMIT
    stdout: int = DEFAULT_FILE_LIMIT
    stderr: int = DEFAULT_FILE_LIMIT
    proc: int = DEFAULT_PROC_LIMIT

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("cpu", mode="before")
    @classmethod
    def ensure_time(cls, v: Any) -> Time:
        if isinstance(v, str):
            return Time(v)
        raise ValueError("Must be a string")

    @field_validator("mem", "stdout", "stderr", mode="before")
    @classmethod
    def ensure_mem(cls, v: Any) -> Memory:
        if isinstance(v, str):
            return Memory(v)
        raise ValueError("Must be a string")


class Parser(str, Enum):
    CLANG_TIDY = "clangtidy"
    CPPCHECK = "cppcheck"
    CPPLINT = "cpplint"
    KEYWORD = "keyword"
    RESULT_STATUS = "result-status"
    RESULT_DETAIL = "result-detail"
    DUMMY = "dummy"
    FILE = "file"
    DIFF = "diff"
    ELF = "elf"


class Stage(BaseModel):
    name: str = ""  # Stage name
    env: List[str] = []
    command: str = ""  # Command to run
    files: StageFiles = StageFiles()
    in_: str = Field("", alias="in")
    out_: str = Field("", alias="out")
    copy_in_cwd: bool = Field(True, alias="copy-in-cwd")
    score: int = 0
    parsers: List[Parser] = []  # list of parsers
    limit: Limit = Limit()
    dummy: ParserDummy = ParserDummy()
    result_status: ParserDummy = Field(ParserDummy(), alias="result-status")
    keyword: ParserKeyword = ParserKeyword()
    clangtidy: ParserKeyword = ParserKeyword()
    cppcheck: ParserKeyword = ParserKeyword()
    cpplint: ParserKeyword = ParserKeyword()
    elf: ParserKeyword = ParserKeyword()
    result_detail: ParserResultDetail = Field(
        ParserResultDetail(), alias="result-detail"
    )
    file: ParserFile = ParserFile()
    skip: List[str] = []

    # cases related
    cases: Dict[str, "Stage"] = {}
    diff: ParserDiff = ParserDiff()

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def gather_cases(cls: Type["Stage"], values: Dict[str, Any]) -> Dict[str, Any]:
        cases = {k: v for k, v in values.items() if k.startswith("case")}
        limit = values.get("limit", {})
        parsed_cases = {}
        for key, case in cases.items():
            case_with_limit = {**limit, **case.get("limit", {})}
            case_for_parsing = {**case, "limit": case_with_limit}
            parsed_cases[key] = case_for_parsing
            values.pop(key)
        values["cases"] = parsed_cases
        return values


class Release(BaseModel):
    end_time: datetime = Field(
        datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc), alias="end-time"
    )  # timestamp = 0, no end time
    begin_time: datetime = Field(
        datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc), alias="begin-time"
    )  # timestamp = 0, no begin time


class Task(BaseModel):
    name: str = "unknown"


class Config(BaseModel):
    root: Path = Path(".")
    path: Path = Path("task.toml")
    task: Task = Task()  # Task name (e.g., hw3 ex5)
    release: Release = Release()  # Release configuration
    stages: List[Stage] = []  # list of stage configurations
