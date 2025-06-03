import socket
from pathlib import Path
from typing import List

from pydantic import AliasChoices, BaseModel, Field


class Files(BaseModel):
    required: List[str] = []
    immutable: List[str] = []


class Groups(BaseModel):
    name: List[str] = []
    max_count: List[int] = Field(
        [], validation_alias=AliasChoices("max-count", "max_count")
    )
    time_period_hour: List[int] = Field(
        [], validation_alias=AliasChoices("time-period-hour", "time_period_hour")
    )


class Config(BaseModel):
    max_size: float = Field(
        10, ge=0, validation_alias=AliasChoices("max-size", "max_size")
    )
    files: Files = Files()
    sandbox_token: str = Field(
        "", validation_alias=AliasChoices("sandbox-token", "sandbox_token")
    )
    max_total_score: int = Field(
        100, validation_alias=AliasChoices("max-total-score", "max_total_score")
    )
    force_skip_health_check_on_test: bool = Field(
        False,
        validation_alias=AliasChoices(
            "force-skip-health-check-on-test", "force_skip_health_check_on_test"
        ),
    )
    force_skip_teapot_on_test: bool = Field(
        False,
        validation_alias=AliasChoices(
            "force-skip-teapot-on-test", "force_skip_teapot_on_test"
        ),
    )
    groups: Groups = Groups()
    root: Path = Path(".")
    path: Path = Path("repo.toml")
    grading_repo_name: str = Field(
        f"{socket.gethostname().split('-')[0]}-joj",
        validation_alias=AliasChoices("grading-repo-name", "grading_repo_name"),
    )
    health_check_score: int = Field(
        0, validation_alias=AliasChoices("health-check-score", "health_check_score")
    )
    submitter_in_issue_title: bool = Field(
        True,
        validation_alias=AliasChoices(
            "submitter-in-issue-title", "submitter_in_issue_title"
        ),
    )
