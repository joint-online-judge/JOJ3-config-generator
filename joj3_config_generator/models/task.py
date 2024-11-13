from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field, root_validator


class ParserResultDetail(BaseModel):
    time: Optional[bool] = True  # Display run time
    mem: Optional[bool] = True  # Display memory usage
    stdout: Optional[bool] = False  # Display stdout messages
    stderr: Optional[bool] = False  # Display stderr messages
    exitstatus: Optional[bool] = False


class ParserDummy(BaseModel):
    comment: Optional[str] = ""
    score: Optional[int] = 0
    forcequit: Optional[bool] = True


class ParserKeyword(BaseModel):
    keyword: Optional[list[str]] = []
    weight: Optional[list[int]] = []


class Outputs(BaseModel):
    score: Optional[int] = 0
    ignorespaces: Optional[bool] = True
    hide: Optional[bool] = False
    forcequit: Optional[bool] = True


class ParserDiff(BaseModel):
    output: Optional[Outputs] = Outputs()


class Files(BaseModel):
    import_: Optional[List[str]] = Field(
        [], serialization_alias="import", validation_alias="import"
    )
    export: Optional[List[str]] = []


class Limit(BaseModel):
    mem: Optional[int] = 800
    cpu: Optional[int] = 1000
    stderr: Optional[int] = 800
    stdout: Optional[int] = 800


class Stage(BaseModel):
    name: Optional[str] = None  # Stage name
    command: Optional[str] = None  # Command to run
    files: Optional[Files] = None
    score: Optional[int] = 0
    parsers: Optional[list[str]] = []  # list of parsers
    limit: Optional[Limit] = Limit()
    dummy: Optional[ParserDummy] = ParserDummy()
    result_status: Optional[ParserDummy] = Field(ParserDummy(), alias="result-status")
    keyword: Optional[ParserKeyword] = ParserKeyword()
    clangtidy: Optional[ParserKeyword] = ParserKeyword()
    cppcheck: Optional[ParserKeyword] = ParserKeyword()
    # FIXME: determine cpplint type
    cpplint: Optional[ParserKeyword] = ParserKeyword()
    result_detail: Optional[ParserResultDetail] = Field(
        ParserResultDetail(), alias="result-detail"
    )
    skip: Optional[list[str]] = []
    diff: Optional[ParserDiff] = ParserDiff()
    cases: Optional[Dict[str, "Stage"]] = {}

    class Config:
        extra = "allow"

    @root_validator(pre=True)
    def gather_cases(cls: Type["Stage"], values: Dict[str, Any]) -> Dict[str, Any]:
        cases = {k: v for k, v in values.items() if k.startswith("case")}
        for key in cases:
            values.pop(key)
        values["cases"] = {k: Stage(**v) for k, v in cases.items()}
        return values


class Release(BaseModel):
    deadline: Optional[datetime]  # RFC 3339 formatted date-time with offset


class Task(BaseModel):
    type_: Optional[str] = Field(
        "", serialization_alias="type", validation_alias="type"
    )
    name: str


class Config(BaseModel):
    task: Task
    release: Release  # Release configuration
    stages: List[Stage]  # list of stage configurations
