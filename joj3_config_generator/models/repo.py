from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class Files(BaseModel):
    whitelist_patterns: List[str]
    whitelist_file: Optional[str]
    required: List[str]
    immutable: List[str]


class Config(BaseModel):
    root: Path = Path(".")
    path: Path = Path("repo.toml")
    teaching_team: List[str]
    max_size: float = Field(..., ge=0)
    release_tags: List[str]
    files: Files
    sandbox_token: str
