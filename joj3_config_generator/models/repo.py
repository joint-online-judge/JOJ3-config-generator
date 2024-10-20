from typing import Optional

from pydantic import BaseModel, Field


class RepoFiles(BaseModel):
    whitelist_patterns: list[str]
    whitelist_file: Optional[str]
    required: list[str]
    immutable: list[str]


class Repo(BaseModel):
    teaching_team: list[str]
    max_size: float = Field(..., ge=0)
    release_tags: list[str]
    files: RepoFiles
    sandbox_token: str
