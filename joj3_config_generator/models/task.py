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


class ParserKeyword(BaseModel):
    keyword: Optional[list[str]] = None
    weight: Optional[list[int]] = None


class Files(BaseModel):
    import_: Optional[List[str]] = Field(serialization_alias="import", validation_alias="import")
    export: Optional[List[str]]



class Limit(BaseModel):
    mem: Optional[int] = 4
    cpu: Optional[int] = 4
    stderr: Optional[int] = 4
    stdout: Optional[int] = 4


class Stage(BaseModel):
    name: str  # Stage name
    command: str  # Command to run
    files: Optional[Files] = None
    score: Optional[int] = 0
    parsers: list[str]  # list of parsers
    limit: Optional[Limit] = None
    dummy: Optional[ParserDummy] = ParserDummy()
    keyword: Optional[ParserKeyword] = ParserKeyword()
    clangtidy: Optional[ParserKeyword] = ParserKeyword()
    cppcheck: Optional[ParserKeyword] = ParserKeyword()
    cpplint: Optional[ParserKeyword] = ParserKeyword()
    result_detail: Optional[ParserResultDetail] = Field(
        ParserResultDetail(), alias="result-detail"
    )


class Release(BaseModel):
    deadline: Optional[datetime]  # RFC 3339 formatted date-time with offset


class Config(BaseModel):
    task: str  # Task name (e.g., hw3 ex5)
    release: Release  # Release configuration
    stages: List[Stage]  # list of stage configurations
