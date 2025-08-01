import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from joj3_config_generator.models.common import Memory, Time
from joj3_config_generator.models.const import (
    DEFAULT_CASE_SCORE,
    DEFAULT_CLOCK_LIMIT_MULTIPLIER,
    DEFAULT_CPU_LIMIT,
    DEFAULT_FILE_LIMIT,
    DEFAULT_MEMORY_LIMIT,
    DEFAULT_PROC_LIMIT,
)
from joj3_config_generator.models.repo import Groups


class ParserResultDetail(BaseModel):
    cpu_time: bool = Field(
        True, validation_alias=AliasChoices("cpu-time", "cpu_time", "cpu")
    )  # Display CPU time
    time: bool = True  # Display wall-clock time
    mem: bool = True  # Display memory usage
    stdout: bool = False  # Display stdout messages
    stderr: bool = False  # Display stderr messages
    exit_status: bool = Field(
        True, validation_alias=AliasChoices("exit-status", "exit_status")
    )  # Display exit status
    proc_peak: bool = Field(
        False, validation_alias=AliasChoices("proc-peak", "proc_peak")
    )  # Display peak process count
    error: bool = False  # Display error messages
    code_block: bool = Field(
        True, validation_alias=AliasChoices("code-block", "code_block")
    )  # Display file in code block
    max_length: int = Field(
        2048, validation_alias=AliasChoices("max-length", "max_length")
    )  # Max output length of each file


class ParserFile(BaseModel):
    name: str = ""


class ParserLog(BaseModel):
    filename: str
    msg: str = ""
    level: str = ""


class ParserDummy(BaseModel):
    comment: str = ""
    score: int = 0
    force_quit: bool = Field(
        False, validation_alias=AliasChoices("force-quit", "force_quit")
    )


class ParserResultStatus(BaseModel):
    comment: str = ""
    score: int = 0
    force_quit: bool = Field(
        True, validation_alias=AliasChoices("force-quit", "force_quit")
    )


class ParserKeyword(BaseModel):
    score: int = 0
    keyword: List[str] = []
    weight: List[int] = []


class ParserDiffOutputs(BaseModel):
    score: int = 0
    ignore_spaces: bool = Field(
        True, validation_alias=AliasChoices("ignore-spaces", "ignore_spaces")
    )
    hide: bool = False
    force_quit: bool = Field(
        False, validation_alias=AliasChoices("force-quit", "force_quit")
    )
    max_length: int = Field(
        2048, validation_alias=AliasChoices("max-length", "max_length")
    )
    max_lines: int = Field(50, validation_alias=AliasChoices("max-lines", "max_lines"))
    hide_common_prefix: bool = Field(
        False, validation_alias=AliasChoices("hide-common-prefix", "hide_common_prefix")
    )


class ParserDiff(BaseModel):
    score: int = DEFAULT_CASE_SCORE
    ignore_spaces: bool = Field(
        True, validation_alias=AliasChoices("ignore-spaces", "ignore_spaces")
    )
    hide: bool = False
    force_quit: bool = Field(
        False, validation_alias=AliasChoices("force-quit", "force_quit")
    )
    max_length: int = Field(
        2048, validation_alias=AliasChoices("max-length", "max_length")
    )
    max_lines: int = Field(50, validation_alias=AliasChoices("max-lines", "max_lines"))
    hide_common_prefix: bool = Field(
        False, validation_alias=AliasChoices("hide-common-prefix", "hide_common_prefix")
    )
    # remove below codes when migration is complete
    output: ParserDiffOutputs = ParserDiffOutputs()
    default_score: int = Field(
        DEFAULT_CASE_SCORE,
        validation_alias=AliasChoices("default-score", "default_score"),
    )

    @model_validator(mode="after")
    def copy_output_fields(self) -> "ParserDiff":
        if "default_score" in self.model_fields_set:
            self.score = self.default_score
        if not isinstance(self.output, ParserDiffOutputs):
            return self
        for field_name, field_value in self.output.model_dump().items():
            if field_name in self.output.model_fields_set and hasattr(self, field_name):
                setattr(self, field_name, field_value)
        return self


class StageFiles(BaseModel):
    import_: List[str] = Field([], validation_alias="import")
    export: List[str] = []
    import_map: Dict[str, str] = Field(
        {}, validation_alias=AliasChoices("import-map", "import_map")
    )


class Limit(BaseModel):
    mem: int = DEFAULT_MEMORY_LIMIT
    cpu: int = DEFAULT_CPU_LIMIT
    time: int = 0
    stdout: int = DEFAULT_FILE_LIMIT
    stderr: int = DEFAULT_FILE_LIMIT
    proc: int = DEFAULT_PROC_LIMIT

    @field_validator("cpu", "time", mode="before")
    @classmethod
    def ensure_time_type(cls, v: Any) -> Time:
        if isinstance(v, str):
            return Time(v)
        raise ValueError(f'Must be a string, e.g., "1s" or "100ms", but got {v}')

    @field_validator("mem", "stdout", "stderr", mode="before")
    @classmethod
    def ensure_mem_type(cls, v: Any) -> Memory:
        if isinstance(v, str):
            return Memory(v)
        raise ValueError(f'Must be a string, e.g., "256m" or "1g", but got {v}')

    @model_validator(mode="after")
    def set_time_if_not_set(self) -> "Limit":
        if self.time == 0:
            self.time = DEFAULT_CLOCK_LIMIT_MULTIPLIER * self.cpu
        return self


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


class Case(BaseModel):
    env: List[str] = []
    command: str = ""  # Command to run
    files: StageFiles = StageFiles()
    in_: str = Field("", validation_alias="in")
    out_: str = Field("", validation_alias="out")
    copy_in_cwd: bool = Field(
        True, validation_alias=AliasChoices("copy-in-cwd", "copy_in_cwd")
    )
    limit: Limit = Limit()
    diff: ParserDiff = ParserDiff()


class Stage(Case):
    name: str = ""  # stage name

    parsers: List[Parser] = []  # list of parsers
    dummy: ParserDummy = ParserDummy()
    result_status: ParserResultStatus = Field(
        ParserResultStatus(),
        validation_alias=AliasChoices("result-status", "result_status"),
    )
    keyword: ParserKeyword = ParserKeyword()
    clangtidy: ParserKeyword = ParserKeyword()
    cppcheck: ParserKeyword = ParserKeyword()
    cpplint: ParserKeyword = ParserKeyword()
    elf: ParserKeyword = ParserKeyword()
    result_detail: ParserResultDetail = Field(
        ParserResultDetail(),
        validation_alias=AliasChoices("result-detail", "result_detail"),
    )
    file: ParserFile = ParserFile()
    # diff: ParserDiff = ParserDiff() # inherited from Case

    cases: Dict[str, Case] = {}

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
        datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        validation_alias=AliasChoices("end-time", "end_time"),
    )  # timestamp = 0, no end time
    begin_time: datetime = Field(
        datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        validation_alias=AliasChoices("begin-time", "begin_time"),
    )  # timestamp = 0, no begin time


class SubmissionTime(BaseModel):
    begin: Optional[datetime] = None
    end: Optional[datetime] = None


class Task(BaseModel):
    name: str = "unknown"


class Penalties(BaseModel):
    hours: List[float] = []
    factors: List[float] = []


class Config(BaseModel):
    root: Path = Field(Path("."), exclude=True)
    path: Path = Field(Path("task.toml"), exclude=True)
    suffix: str = Field("", exclude=True)

    task: Task = Task()  # TODO: remove it in the future
    name: str = "unknown"  # Task name (e.g., hw3 ex5)
    max_total_score: Optional[int] = Field(
        None, validation_alias=AliasChoices("max-total-score", "max_total_score")
    )
    scoreboard: str = "scoreboard.csv"
    scoreboard_column_by_ref: bool = Field(
        False,
        validation_alias=AliasChoices(
            "scoreboard-column-by-ref", "scoreboard_column_by_ref"
        ),
    )
    time: SubmissionTime = SubmissionTime()  # Valid time configuration
    release: Release = Release()  # Release configuration
    groups: Groups = Groups()
    penalties: Penalties = Penalties()
    stages: List[Stage] = []  # list of stage configurations

    # TODO: remove this validator in the future
    @model_validator(mode="after")
    def set_name(self) -> "Config":
        if "task" in self.model_fields_set and "name" in self.task.model_fields_set:
            self.name = self.task.name
        return self

    @model_validator(mode="after")
    def set_suffix(self) -> "Config":
        if not self.suffix:
            self.suffix = re.split(r"[-_/\s]+", self.name)[0]
        return self

    @model_validator(mode="after")
    def set_scoreboard(self) -> "Config":
        if self.scoreboard == "auto":
            self.scoreboard = f"scoreboard-{self.suffix}.csv"
        return self
