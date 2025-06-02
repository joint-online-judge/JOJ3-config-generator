import socket
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field


class Files(BaseModel):
    required: List[str] = []
    immutable: List[str] = []


class Groups(BaseModel):
    name: List[str] = []
    max_count: List[int] = Field([], alias="max-count")
    time_period_hour: List[int] = Field([], alias="time-period-hour")


class Config(BaseModel):
    max_size: float = Field(10, ge=0, alias="max-size")
    files: Files = Files()
    sandbox_token: str = Field("", alias="sandbox-token")
    max_total_score: int = Field(100, alias="max-total-score")
    force_skip_health_check_on_test: bool = Field(
        False, alias="force-skip-health-check-on-test"
    )
    force_skip_teapot_on_test: bool = Field(False, alias="force-skip-teapot-on-test")
    groups: Groups = Groups()
    root: Path = Path(".")
    path: Path = Path("repo.toml")
    grading_repo_name: str = Field(
        f"{socket.gethostname().split('-')[0]}-joj", alias="grading-repo-name"
    )
    health_check_score: int = Field(0, alias="health-check-score")
    submitter_in_issue_title: bool = Field(True, alias="submitter-in-issue-title")
