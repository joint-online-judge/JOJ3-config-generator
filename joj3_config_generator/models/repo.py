from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class Files(BaseModel):
    required: List[str] = []
    immutable: List[str] = []


class Groups(BaseModel):
    name: List[str] = []
    max_count: List[int] = []
    time_period_hour: List[int] = []


class Config(BaseModel):
    max_size: float = Field(10, ge=0)
    files: Files = Files()
    sandbox_token: str = Field("")
    max_total_score: int = Field(100)
    force_skip_heatlh_check_on_test: bool = False
    groups: Groups = Groups()
    root: Path = Path(".")
    path: Path = Path("repo.toml")
