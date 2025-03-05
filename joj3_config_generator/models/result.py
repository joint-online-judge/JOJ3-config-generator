from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from joj3_config_generator.models.const import (
    DEFAULT_CPU_LIMIT,
    DEFAULT_FILE_LIMIT,
    DEFAULT_MEMORY_LIMIT,
)


class LocalFile(BaseModel):
    src: str


class MemoryFile(BaseModel):
    content: str


class PreparedFile(BaseModel):
    file_id: str = Field(..., alias="fileId")


class Collector(BaseModel):
    name: str
    max: int = DEFAULT_FILE_LIMIT
    pipe: bool = True


class Symlink(BaseModel):
    symlink: str


class StreamIn(BaseModel):
    stream_in: bool = Field(..., alias="streamIn")


class StreamOut(BaseModel):
    stream_out: bool = Field(..., alias="streamOut")


InputFile = Union[LocalFile, MemoryFile, PreparedFile, Symlink]


class Cmd(BaseModel):
    args: List[str] = []
    env: List[str] = []
    stdin: Union[InputFile, StreamIn] = MemoryFile(content="")
    stdout: Union[Collector, StreamOut] = Collector(name="stdout")
    stderr: Union[Collector, StreamOut] = Collector(name="stderr")
    cpu_limit: int = Field(DEFAULT_CPU_LIMIT, serialization_alias="cpuLimit")
    clock_limit: int = Field(2 * DEFAULT_CPU_LIMIT, serialization_alias="clockLimit")
    memory_limit: int = Field(DEFAULT_MEMORY_LIMIT, serialization_alias="memoryLimit")
    stack_limit: int = Field(0, serialization_alias="stackLimit")
    proc_limit: int = Field(50, serialization_alias="procLimit")
    cpu_rate_limit: int = Field(0, serialization_alias="cpuRateLimit")
    cpu_set_limit: str = Field("", serialization_alias="cpuSetLimit")
    copy_in: Dict[str, InputFile] = Field({}, serialization_alias="copyIn")
    copy_in_cached: Dict[str, str] = Field({}, serialization_alias="copyInCached")
    copy_in_dir: str = Field(".", serialization_alias="copyInDir")
    copy_out: List[str] = Field(["stdout", "stderr"], serialization_alias="copyOut")
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
    stdin: Optional[Union[InputFile, StreamIn]] = None
    stdout: Optional[Union[Collector, StreamOut]] = None
    stderr: Optional[Union[Collector, StreamOut]] = None
    cpu_limit: Optional[int] = Field(None, serialization_alias="cpuLimit")
    clock_limit: Optional[int] = Field(None, serialization_alias="clockLimit")
    memory_limit: Optional[int] = Field(None, serialization_alias="memoryLimit")
    stack_limit: Optional[int] = Field(None, serialization_alias="stackLimit")
    proc_limit: Optional[int] = Field(None, serialization_alias="procLimit")
    cpu_rate_limit: Optional[int] = Field(None, serialization_alias="cpuRateLimit")
    cpu_set_limit: Optional[str] = Field(None, serialization_alias="cpuSetLimit")
    copy_in: Optional[Dict[str, InputFile]] = Field(None, serialization_alias="copyIn")
    copy_in_cached: Optional[Dict[str, str]] = Field(
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


class ExecutorWith(BaseModel):
    default: Cmd = Cmd()
    cases: List[OptionalCmd] = []


class Executor(BaseModel):
    name: str
    with_: ExecutorWith = Field(ExecutorWith(), serialization_alias="with")


class Parser(BaseModel):
    name: str
    if TYPE_CHECKING:

        class Empty(BaseModel):
            pass

        with_: BaseModel = Field(Empty(), serialization_alias="with")
    else:
        with_: Dict[str, Any] = Field({}, serialization_alias="with")

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("with_", mode="before")
    @classmethod
    def validate_with(cls, v: Any) -> Dict[str, Any]:
        if isinstance(v, BaseModel):
            return v.model_dump(by_alias=True)
        raise ValueError("Must be a BaseModel instance")


class StageDetail(BaseModel):
    name: str
    group: str = ""
    executor: Executor
    parsers: List[Parser]


class Stage(BaseModel):
    sandbox_exec_server: str = Field(
        "172.17.0.1:5051", serialization_alias="sandboxExecServer"
    )
    sandbox_token: str = Field("", serialization_alias="sandboxToken")
    output_path: str = Field(
        "/tmp/joj3_result.json", serialization_alias="outputPath"
    )  # nosec: B108
    stages: List[StageDetail] = []
    pre_stages: List[StageDetail] = Field([], serialization_alias="preStages")
    post_stages: List[StageDetail] = Field([], serialization_alias="postStages")


class Config(BaseModel):
    name: str = ""
    log_path: str = Field("", serialization_alias="logPath")
    expire_unix_timestamp: int = Field(-1, serialization_alias="expireUnixTimestamp")
    effective_unix_timestamp: int = Field(
        -1, serialization_alias="effectiveUnixTimestamp"
    )
    actor_csv_path: str = Field("", serialization_alias="actorCsvPath")
    max_total_score: int = Field(100, serialization_alias="maxTotalScore")
    stage: Stage


class DummyConfig(BaseModel):
    score: int = 0
    comment: Optional[str] = None
    force_quit_on_not_accepted: Optional[bool] = Field(
        False, serialization_alias="forceQuitOnNotAccepted"
    )


class DiffOutputConfig(BaseModel):
    score: int = 100
    file_name: str = Field("", serialization_alias="fileName")
    answer_path: str = Field("", serialization_alias="answerPath")
    force_quit_on_diff: bool = Field(False, serialization_alias="forceQuitOnDiff")
    always_hide: bool = Field(False, serialization_alias="alwaysHide")
    compare_space: bool = Field(False, serialization_alias="compareSpace")


class ResultDetailConfig(BaseModel):
    score: int = 0
    comment: str = ""
    show_files: List[str] = Field([], serialization_alias="showFiles")
    show_exit_status: bool = Field(True, serialization_alias="showExitStatus")
    show_runtime: bool = Field(True, serialization_alias="showRuntime")
    show_memory: bool = Field(False, serialization_alias="showMemory")


class KeywordConfig(BaseModel):
    keywords: List[str] = []
    score: int = 0


class KeywordMatchConfig(BaseModel):
    matches: List[KeywordConfig] = []


class FileConfig(BaseModel):
    name: str = ""


class DiffCasesConfig(BaseModel):
    outputs: List[DiffOutputConfig] = []


class DiffConfig(BaseModel):
    name: str = "diff"
    cases: List[DiffCasesConfig] = []


class MsgConfig(BaseModel):
    msg: str = ""


class ScoreConfig(BaseModel):
    score: int = 0
