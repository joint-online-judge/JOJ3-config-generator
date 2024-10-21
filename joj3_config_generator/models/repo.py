from typing import List, Optional

from pydantic import BaseModel, Field


class RepoFiles(BaseModel):
    whitelist_patterns: List[str]
    whitelist_file: Optional[str]
    required: List[str]
    immutable: List[str]


class RepoConfig(BaseModel):
    teaching_team: List[str]
    max_size: float = Field(..., ge=0)
    release_tags: List[str]
    files: RepoFiles
    sandbox_token: str
