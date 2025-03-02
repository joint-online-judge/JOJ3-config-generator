import hashlib
from pathlib import Path
from typing import List

from joj3_config_generator.models import repo, result
from joj3_config_generator.models.const import CACHE_ROOT, TEAPOT_CONFIG_ROOT


def get_teapot_stage(repo_conf: repo.Config) -> result.StageDetail:
    args = [
        "/usr/local/bin/joint-teapot",
        "joj3-all-env",
        str(TEAPOT_CONFIG_ROOT / "teapot.env"),
        "--grading-repo-name",
        repo_conf.grading_repo_name,
        "--max-total-score",
        str(repo_conf.max_total_score),
    ]

    stage_conf = result.StageDetail(
        name="teapot",
        executor=result.Executor(
            name="local",
            with_=result.ExecutorWith(
                default=result.Cmd(
                    args=args,
                    env=[f"LOG_FILE_PATH={CACHE_ROOT}/joint-teapot-debug.log"],
                ),
                cases=[],
            ),
        ),
        parsers=[result.ParserConfig(name="log", with_={"msg": "joj3 summary"})],
    )
    return stage_conf


def get_healthcheck_args(repo_conf: repo.Config) -> List[str]:
    return [
        "/usr/local/bin/repo-health-checker",
        "-root=.",
        f"-repoSize={str(repo_conf.max_size)}",
        *[f"-meta={meta}" for meta in repo_conf.files.required],
        get_hash(repo_conf),
        f"-checkFileNameList={','.join(repo_conf.files.immutable)}",
    ]


def get_debug_args(repo_conf: repo.Config) -> List[str]:
    group_config = ""
    for i, name in enumerate(repo_conf.groups.name):
        group_config = (
            group_config
            + f"{name}="
            + f"{repo_conf.groups.max_count[i]}:"
            + f"{repo_conf.groups.time_period_hour[i]},"
        )
    # default value hardcoded
    group_config = group_config + "=100:24"
    return [
        "/usr/local/bin/joint-teapot",
        "joj3-check-env",
        str(TEAPOT_CONFIG_ROOT / "teapot.env"),
        "--grading-repo-name",
        repo_conf.grading_repo_name,
        "--group-config",
        group_config,
    ]


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
                        args=get_healthcheck_args(repo_conf),
                    ),
                    result.OptionalCmd(
                        args=get_debug_args(repo_conf),
                        env=[f"LOG_FILE_PATH={CACHE_ROOT}/joint-teapot-debug.log"],
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


def calc_sha256sum(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536 * 2), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_hash(repo_conf: repo.Config) -> str:  # input should be a list
    base_dir = (repo_conf.root / repo_conf.path).parent
    immutable_dir = base_dir / "immutable_files"
    immutable_files = [
        immutable_dir / Path(file).name for file in repo_conf.files.immutable
    ]
    immutable_hash = [calc_sha256sum(file) for file in immutable_files]
    return f"-checkFileSumList={','.join(immutable_hash)}"
