import os
from pathlib import Path
from typing import List

from pydantic import AliasChoices, BaseModel, Field, model_validator


class Files(BaseModel):
    required: List[str] = []
    # TODO: remove immutable in the future
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
    groups: Groups = Groups()
    health_check_score: int = Field(
        0, validation_alias=AliasChoices("health-check-score", "health_check_score")
    )
    issue: Issue = Issue()
    immutable_path: Path = Field(
        Path("immutable"),
        validation_alias=AliasChoices("immutable-path", "immutable_path"),
    )
    grading_repo_name: str = Field(
        "",
        validation_alias=AliasChoices("grading-repo-name", "grading_repo_name"),
    )
    # TODO: remove gitea_token and gitea_org in the future
    gitea_token: str = Field(
        "", validation_alias=AliasChoices("gitea-token", "gitea_token")
    )
    gitea_org: str = Field("", validation_alias=AliasChoices("gitea-org", "gitea_org"))

    @model_validator(mode="after")
    def set_grading_repo_name_from_cwd(self) -> "Config":
        if not self.grading_repo_name:
            course_env = os.getenv("COURSE")
            if course_env:
                self.grading_repo_name = f"{course_env}-joj"
            else:
                self.grading_repo_name = Path.cwd().name
        return self
