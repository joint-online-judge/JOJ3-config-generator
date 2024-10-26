from datetime import datetime
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field, root_validator


class ParserResultDetail(BaseModel):
    time: Optional[bool] = True  # Display run time
    mem: Optional[bool] = True  # Display memory usage
    stdout: Optional[bool] = False  # Display stdout messages
    stderr: Optional[bool] = False  # Display stderr messages
    exitstatus: Optional[bool] = False


class ParserDummy(BaseModel):
    comment: Optional[str] = ""


class ParserKeyword(BaseModel):
    keyword: Optional[list[str]] = []
    weight: Optional[list[int]] = []


class Outputs(BaseModel):
    score: Optional[int] = 0
    ignorespaces: Optional[bool] = False
    hide: Optional[bool] = False
    forcequit: Optional[bool] = True


class ParserDiff(BaseModel):
    output: Optional[Outputs] = Outputs()


class Files(BaseModel):
    import_: Optional[list[str]] = Field([], alias="import")
    export: Optional[list[str]] = []


class Limit(BaseModel):
    mem: Optional[int] = 4
    cpu: Optional[int] = 4
    stderr: Optional[int] = 4
    stdout: Optional[int] = 4


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
    # cpplint: Optional[ParserKeyword] = ParserKeyword()
    cpplint: Optional[ParserDummy] = ParserDummy()
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
    task: str  # Task name (e.g., hw3 ex5)
    release: Release  # Release configuration
    stages: list[Stage]  # list of stage configurations
