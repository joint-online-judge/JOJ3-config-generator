import hashlib
import os
import tempfile

from dotenv import load_dotenv

from joj3_config_generator.models import (
    Cmd,
    CmdFile,
    ExecutorConfig,
    ExecutorWithConfig,
    ParserConfig,
    Repo,
    ResultConfig,
    Stage,
    StageConfig,
    Task,
    TeapotConfig,
)


def get_temp_directory() -> str:
    return tempfile.mkdtemp(prefix="repo-checker-")


def getGradingRepoName() -> str:
    path = os.path.expanduser("~/.config/teapot/teapot.env")
    if os.path.exists(path):
        load_dotenv(path)
        repo_name = os.environ.get("GITEA_ORG_NAME")
        if repo_name is not None:
            return f"{repo_name.split('-')[0]}-joj"
    return "ece482-joj"


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
    chore = f"/{get_temp_directory}/repo-health-checker -root=. "
    args = ""
    args = args + chore
    args = args + repo_size
    for meta in required_files:
        args = args + meta

    args = args + get_hash(immutable)

    args = args + immutable_files

    cmd = Cmd(
        args=args.split(),
        # FIXME: easier to edit within global scope
        copy_in={
            f"/{get_temp_directory()}/repo-health-checker": CmdFile(
                src=f"/{get_temp_directory()}/repo-health-checker"
            )
        },
    )
    return cmd


def getHealthcheckConfig(repo_conf: Repo, task_conf: Task) -> Stage:
    healthcheck_stage = Stage(
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
    file_path = "../immutable_file/"  # TODO: change this when things are on the server
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