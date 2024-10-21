from typing import Any, List, Optional

import rtoml
from pydantic import BaseModel, Field


class CmdFile(BaseModel):
    src: Optional[str] = None
    content: Optional[str] = None
    file_id: Optional[str] = Field(None, serialization_alias="fileId")
    name: Optional[str] = None
    max: Optional[int] = None
    symlink: Optional[str] = None
    stream_in: bool = Field(False, serialization_alias="streamIn")
    stream_out: bool = Field(False, serialization_alias="streamOut")
    pipe: bool = False


class Cmd(BaseModel):
    args: List[str]
    env: List[str] = []
    stdin: Optional[CmdFile] = None
    stdout: Optional[CmdFile] = None
    stderr: Optional[CmdFile] = None
    cpu_limit: int = Field(0, serialization_alias="cpuLimit")
    real_cpu_limit: int = Field(0, serialization_alias="realCpuLimit")
    clock_limit: int = Field(0, serialization_alias="clockLimit")
    memory_limit: int = Field(0, serialization_alias="memoryLimit")
    stack_limit: int = Field(0, serialization_alias="stackLimit")
    proc_limit: int = Field(0, serialization_alias="procLimit")
    cpu_rate_limit: int = Field(0, serialization_alias="cpuRateLimit")
    cpu_set_limit: str = Field("", serialization_alias="cpuSetLimit")
    copy_in: dict[str, CmdFile] = Field({}, serialization_alias="copyIn")
    copy_in_cached: dict[str, str] = Field({}, serialization_alias="copyInCached")
    copy_in_dir: str = Field(".", serialization_alias="copyInDir")
    copy_out: List[str] = Field([], serialization_alias="copyOut")
    copy_out_cached: List[str] = Field([], serialization_alias="copyOutCached")
    copy_out_max: int = Field(0, serialization_alias="copyOutMax")
    copy_out_dir: str = Field("", serialization_alias="copyOutDir")
    tty: bool = False
    strict_memory_limit: bool = Field(False, serialization_alias="strictMemoryLimit")
    data_segment_limit: bool = Field(False, serialization_alias="dataSegmentLimit")
    address_space_limit: bool = Field(False, serialization_alias="addressSpaceLimit")


class OptionalCmd(BaseModel):
    args: Optional[List[str]] = None
    env: Optional[List[str]] = None
    stdin: Optional[CmdFile] = None
    stdout: Optional[CmdFile] = None
    stderr: Optional[CmdFile] = None
    cpu_limit: Optional[int] = Field(None, serialization_alias="cpuLimit")
    real_cpu_limit: Optional[int] = Field(None, serialization_alias="realCpuLimit")
    clock_limit: Optional[int] = Field(None, serialization_alias="clockLimit")
    memory_limit: Optional[int] = Field(None, serialization_alias="memoryLimit")
    stack_limit: Optional[int] = Field(None, serialization_alias="stackLimit")
    proc_limit: Optional[int] = Field(None, serialization_alias="procLimit")
    cpu_rate_limit: Optional[int] = Field(None, serialization_alias="cpuRateLimit")
    cpu_set_limit: Optional[str] = Field(None, serialization_alias="cpuSetLimit")
    copy_in: Optional[dict[str, CmdFile]] = Field(None, serialization_alias="copyIn")
    copy_in_cached: Optional[dict[str, str]] = Field(
        None, serialization_alias="copyInCached"
    )
    copy_in_dir: Optional[str] = Field(None, serialization_alias="copyInDir")
    copy_out: Optional[List[str]] = Field(None, serialization_alias="copyOut")
    copy_out_cached: Optional[List[str]] = Field(
        None, serialization_alias="copyOutCached"
    )
    copy_out_max: Optional[int] = Field(None, serialization_alias="copyOutMax")
    copy_out_dir: Optional[str] = Field(None, serialization_alias="copyOutDir")
    tty: Optional[bool] = None
    strict_memory_limit: Optional[bool] = Field(
        None, serialization_alias="strictMemoryLimit"
    )
    data_segment_limit: Optional[bool] = Field(
        None, serialization_alias="dataSegmentLimit"
    )
    address_space_limit: Optional[bool] = Field(
        None, serialization_alias="addressSpaceLimit"
    )


class Stage(BaseModel):
    name: str
    group: str
    executor: "ExecutorConfig"
    parsers: List["ParserConfig"]


class ExecutorWithConfig(BaseModel):
    default: Cmd
    cases: List[OptionalCmd]


class ExecutorConfig(BaseModel):
    name: str
    with_: ExecutorWithConfig = Field(..., serialization_alias="with")


class ParserConfig(BaseModel):
    name: str
    with_: dict[str, Any] = Field(..., serialization_alias="with")


class StageConfig(BaseModel):
    sandbox_exec_server: str = Field(
        "172.17.0.1:5051", serialization_alias="sandboxExecServer"
    )
    sandbox_token: str = Field("", serialization_alias="sandboxToken")
    output_path: str = Field(
        "/tmp/joj3_result.json", serialization_alias="outputPath"
    )  # nosec: B108
    stages: List[Stage]


class TeapotConfig(BaseModel):
    log_path: str = Field(
        "/home/tt/.cache/joint-teapot-debug.log", serialization_alias="logPath"
    )
    scoreboard_path: str = Field("scoreboard.csv", serialization_alias="scoreboardPath")
    failed_table_path: str = Field(
        "failed-table.md", serialization_alias="failedTablePath"
    )
    grading_repo_name: str = Field("", serialization_alias="gradingRepoName")
    skip_issue: bool = Field(False, serialization_alias="skipIssue")
    skip_scoreboard: bool = Field(False, serialization_alias="skipScoreboard")
    skip_failed_table: bool = Field(False, serialization_alias="skipFailedTable")


class ResultConfig(BaseModel):
    name: str = "unknown"
    log_path: str = Field("", serialization_alias="logPath")
    expire_unix_timestamp: int = Field(-1, serialization_alias="expireUnixTimestamp")
    stage: StageConfig
    teapot: TeapotConfig
