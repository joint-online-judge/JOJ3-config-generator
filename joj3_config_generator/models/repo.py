import socket
from pathlib import Path
from typing import List

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
    force_skip_health_check_on_test: bool = False
    force_skip_teapot_on_test: bool = False
    groups: Groups = Groups()
    root: Path = Path(".")
    path: Path = Path("repo.toml")
    grading_repo_name: str = f"{socket.gethostname().split('-')[0]}-joj"
    health_check_score: int = Field(0)
    submitter_in_issue_title: bool = True
