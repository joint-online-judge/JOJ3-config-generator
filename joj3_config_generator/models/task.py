from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ParserResultDetail(BaseModel):
    time: bool = True  # Display run time
    mem: bool = True  # Display memory usage
    stdout: bool = False  # Display stdout messages
    stderr: bool = False  # Display stderr messages


class Files(BaseModel):
    import_: list[str] = Field(alias="import")
    export: list[str]


class Stage(BaseModel):
    name: str  # Stage name
    command: str  # Command to run
    files: Files  # Files to import and export
    score: int  # Score for the task
    parsers: list[str]  # list of parsers
    result_detail: ParserResultDetail = (
        ParserResultDetail()
    )  #  for result-detail parser


class Release(BaseModel):
    deadline: Optional[datetime]  # RFC 3339 formatted date-time with offset


class Task(BaseModel):
    task: str  # Task name (e.g., hw3 ex5)
    release: Release  # Release configuration
    stages: list[Stage]  # list of stage configurations
