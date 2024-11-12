import hashlib
import shlex
import socket
from pathlib import Path

from joj3_config_generator.models import repo, result, task


def getGradingRepoName() -> str:
    host_name = socket.gethostname()
    return f"{host_name.split('-')[0]}-joj"


def getTeapotConfig(repo_conf: Repo, task_conf: Task) -> TeapotConfig:
    teapot = TeapotConfig(
        # TODO: fix the log path
        log_path=f"{task_conf.task.replace(' ', '-')}-joint-teapot-debug.log",
        scoreboard_path=f"{task_conf.task.replace(' ', '-')}-scoreboard.csv",
        failed_table_path=f"{task_conf.task.replace(' ', '-')}-failed-table.md",
        grading_repo_name=getGradingRepoName(),
    )
    return teapot


def getHealthcheckCmd(repo_conf: Repo) -> Cmd:
    repoSize = repo_conf.max_size
    immutable = repo_conf.files.immutable
    repo_size = f"-repoSize={str(repoSize)} "
    required_files = repo_conf.files.required

    for i, meta in enumerate(required_files):
        required_files[i] = f"-meta={meta} "

    immutable_files = f"-checkFileNameList="
    for i, name in enumerate(immutable):
        if i == len(immutable) - 1:
            immutable_files = immutable_files + name + " "
        else:
            immutable_files = immutable_files + name + ","
    # FIXME: need to make solution and make things easier to edit with global scope
    chore = f"./repo-health-checker -root=. "
    args = ""
    args = args + chore
    args = args + repo_size
    for meta in required_files:
        args = args + meta

    args = args + get_hash(immutable)

    args = args + immutable_files

    cmd = result.Cmd(
        args=shlex.split(args),
        # FIXME: easier to edit within global scope
        copy_in={
            f"./repo-health-checker": result.CmdFile(src=f"./repo-health-checker")
        },
    )
    return cmd


def getHealthcheckConfig(repo_conf: repo.Config) -> result.StageDetail:
    healthcheck_stage = result.StageDetail(
        name="healthcheck",
        group="",
        executor=ExecutorConfig(
            name="sandbox",
            with_=ExecutorWithConfig(default=getHealthcheckCmd(repo_conf), cases=[]),
        ),
        parsers=[ParserConfig(name="healthcheck", with_={"score": 0, "comment": ""})],
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
    file_path = f"{project_root}/tests/immutable_file/"
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
