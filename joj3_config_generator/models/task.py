from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class ParserResultDetail(BaseModel):
    time: bool = True  # Display run time
    mem: bool = True  # Display memory usage
    stdout: bool = False  # Display stdout messages
    stderr: bool = False  # Display stderr messages


class Files(BaseModel):
    import_: List[str] = Field(serialization_alias="import", validation_alias="import")
    export: List[str]


class Stage(BaseModel):
    name: str  # Stage name
    command: str  # Command to run
    files: Files  # Files to import and export
    score: int  # Score for the task
    parsers: List[str]  # list of parsers
    result_detail: ParserResultDetail = (
        ParserResultDetail()
    )  #  for result-detail parser


class Release(BaseModel):
    deadline: Optional[datetime]  # RFC 3339 formatted date-time with offset


class Config(BaseModel):
    root: Path = Path(".")
    path: Path = Path("task.toml")
    task: str  # Task name (e.g., hw3 ex5)
    release: Release  # Release configuration
    stages: List[Stage]  # list of stage configurations
