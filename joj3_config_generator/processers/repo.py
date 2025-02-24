import hashlib
import shlex
import socket
from pathlib import Path

from joj3_config_generator.models import repo, result


def get_grading_repo_name() -> str:
    # FIXME: uncomment back when everything is ready!
    # host_name = "engr151"
    host_name = socket.gethostname()
    return f"{host_name.split('-')[0]}-joj"


def get_teapot_stage(repo_conf: repo.Config) -> result.StageDetail:
    args_ = ""
    args_ = (
        args_
        + f"/usr/local/bin/joint-teapot joj3-all-env /home/tt/.config/teapot/teapot.env --grading-repo-name {get_grading_repo_name()} --max-total-score {repo_conf.max_total_score}"
    )

    stage_conf = result.StageDetail(
        name="teapot",
        executor=result.Executor(
            name="local",
            with_=result.ExecutorWith(
                default=result.Cmd(
                    args=shlex.split(args_),
                    env=["LOG_FILE_PATH=/home/tt/.cache/joint-teapot-debug.log"],
                ),
                cases=[],
            ),
        ),
        parsers=[result.ParserConfig(name="log", with_={"msg": "joj3 summary"})],
    )
    return stage_conf


def get_healthcheck_args(repo_conf: repo.Config) -> str:
    repoSize = repo_conf.max_size
    immutable = repo_conf.files.immutable
    repo_size = f"-repoSize={str(repoSize)} "
    required_files = repo_conf.files.required

    for i, meta in enumerate(required_files):
        required_files[i] = f"-meta={meta} "

    immutable_files = "-checkFileNameList="
    for i, name in enumerate(immutable):
        if i == len(immutable) - 1:
            immutable_files = immutable_files + name + " "
        else:
            immutable_files = immutable_files + name + ","
    chore = "/usr/local/bin/repo-health-checker -root=. "
    args = ""
    args = args + chore
    args = args + repo_size
    for meta in required_files:
        args = args + meta

    args = args + get_hash(immutable)

    args = args + immutable_files

    return args


def get_debug_args(repo_conf: repo.Config) -> str:
    args = ""
    args = (
        args
        + f"/usr/local/bin/joint-teapot joj3-check-env /home/tt/.config/teapot/teapot.env --grading-repo-name {get_grading_repo_name()} --group-config "
    )
    group_config = ""
    for i, name in enumerate(repo_conf.groups.name):
        group_config = (
            group_config
            + f"{name}={repo_conf.groups.max_count[i]}:{repo_conf.groups.time_period_hour[i]},"
        )
    # default value hardcoded
    group_config = group_config + "=100:24"
    args = args + group_config
    return args


def get_healthcheck_config(repo_conf: repo.Config) -> result.StageDetail:
    healthcheck_stage = result.StageDetail(
        name="healthcheck",
        group="",
        executor=result.Executor(
            name="local",
            with_=result.ExecutorWith(
                default=result.Cmd(),
                cases=[
                    result.OptionalCmd(
                        args=shlex.split(get_healthcheck_args(repo_conf)),
                    ),
                    result.OptionalCmd(
                        args=shlex.split(get_debug_args(repo_conf)),
                        env=[
                            f"LOG_FILE_PATH={Path.home()}/.cache/joint-teapot-debug.log"
                        ],
                    ),
                ],
            ),
        ),
        parsers=[
            result.ParserConfig(name="healthcheck", with_={"score": 1}),
            result.ParserConfig(name="debug", with_={"score": 0}),
        ],
    )
    return healthcheck_stage


def calc_sha256sum(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536 * 2), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_hash(immutable_files: list[str]) -> str:  # input should be a list
    # FIXME: should be finalized when get into the server
    current_file_path = Path(__file__).resolve()
    project_root = current_file_path.parents[2]
    file_path = f"{project_root}/tests/immutable_p3-test/"
    # default value as hardcoded
    # file_path = "{Path.home()}/.cache/immutable"
    immutable_hash = []
    for i, file in enumerate(immutable_files):
        immutable_files[i] = file_path + file.rsplit("/", 1)[-1]

    for i, file in enumerate(immutable_files):
        immutable_hash.append(calc_sha256sum(file))

    hash_check = "-checkFileSumList="

    for i, file in enumerate(immutable_hash):
        if i == len(immutable_hash) - 1:
            hash_check = hash_check + file + " "
        else:
            hash_check = hash_check + file + ","
    return hash_check
