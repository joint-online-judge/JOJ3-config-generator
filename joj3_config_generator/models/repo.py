import os
from pathlib import Path
from typing import Any, List

from pydantic import AliasChoices, BaseModel, Field, field_validator, model_validator

from joj3_config_generator.models.common import Memory


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


class Label(BaseModel):
    name: str = "Kind/Testing"
    color: str = "#795548"
    exclusive: bool = False


class Issue(BaseModel):
    label: Label = Label()
    show_submitter: bool = Field(
        True, validation_alias=AliasChoices("show-submitter", "show_submitter")
    )


class HealthCheck(BaseModel):
    score: int = 0
    max_size: int = Field(
        Memory("10m"), validation_alias=AliasChoices("max-size", "max_size")
    )
    immutable_path: Path = Field(
        Path("immutable"),
        validation_alias=AliasChoices("immutable-path", "immutable_path"),
    )
    required_files: List[str] = Field(
        [], validation_alias=AliasChoices("required-files", "required_files")
    )

    @field_validator("max_size", mode="before")
    @classmethod
    def ensure_mem_type(cls, v: Any) -> Memory:
        if isinstance(v, str):
            return Memory(v)
        raise ValueError(f'Must be a string, e.g., "256m" or "1g", but got {v}')


class Config(BaseModel):
    root: Path = Field(Path("."), exclude=True)
    path: Path = Field(Path("repo.toml"), exclude=True)

    force_skip_health_check_on_test: bool = Field(
        False,
        validation_alias=AliasChoices(
            "force-skip-health-check-on-test", "force_skip_health_check_on_test"
        ),
        exclude=True,
    )
    force_skip_teapot_on_test: bool = Field(
        False,
        validation_alias=AliasChoices(
            "force-skip-teapot-on-test", "force_skip_teapot_on_test"
        ),
        exclude=True,
    )
    grading_repo_name: str = Field(
        "",
        validation_alias=AliasChoices("grading-repo-name", "grading_repo_name"),
    )
    sandbox_token: str = Field(
        "", validation_alias=AliasChoices("sandbox-token", "sandbox_token")
    )
    max_total_score: int = Field(
        100, validation_alias=AliasChoices("max-total-score", "max_total_score")
    )
    groups: Groups = Groups()
    issue: Issue = Issue()

    health_check: HealthCheck = Field(
        HealthCheck(), validation_alias=AliasChoices("health-check", "health_check")
    )

    @model_validator(mode="after")
    def set_grading_repo_name_from_cwd(self) -> "Config":
        if not self.grading_repo_name:
            course_env = os.getenv("COURSE")
            if course_env:
                self.grading_repo_name = f"{course_env}-joj"
            else:
                self.grading_repo_name = Path.cwd().name
        return self
