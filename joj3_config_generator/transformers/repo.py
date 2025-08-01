import hashlib
import sys
from pathlib import Path
from typing import List, Tuple

from joj3_config_generator.models import common, repo, result, task
from joj3_config_generator.models.const import (
    CACHE_ROOT,
    TEAPOT_CONFIG_ROOT,
    TEAPOT_LOG_PATH,
)
from joj3_config_generator.utils.logger import logger


def get_teapot_env(repo_conf: repo.Config) -> List[str]:
    res = [
        f"REPOS_DIR={CACHE_ROOT}",
        f"LOG_FILE_PATH={TEAPOT_LOG_PATH}",
    ]
    if repo_conf.gitea_org:
        res.append(f"GITEA_ORG_NAME={repo_conf.gitea_org}")
    if repo_conf.gitea_token:
        res.append(f"GITEA_ACCESS_TOKEN={repo_conf.gitea_token}")
    return res


def get_teapot_post_stage(
    repo_conf: repo.Config, task_conf: task.Config
) -> result.StageDetail:
    args = [
        "/usr/local/bin/joint-teapot",
        "joj3-all-env",
        str(TEAPOT_CONFIG_ROOT / "teapot.env"),
        "--grading-repo-name",
        repo_conf.grading_repo_name,
        "--max-total-score",
        (
            str(task_conf.max_total_score)
            if task_conf.max_total_score is not None
            else str(repo_conf.max_total_score)
        ),
        "--issue-label-name",
        repo_conf.issue.label.name,
        "--issue-label-color",
        repo_conf.issue.label.color,
        "--scoreboard-filename",
        task_conf.scoreboard,
    ]
    if task_conf.scoreboard_column_by_ref:
        args.append("--scoreboard-column-by-ref")
    if repo_conf.issue.label.exclusive:
        args.append("--issue-label-exclusive")
    if not repo_conf.issue.show_submitter:
        args.append("--no-submitter-in-issue-title")
    if task_conf.time.end:
        args.extend(
            [
                "--end-time",
                task_conf.time.end.strftime("%Y-%m-%dT%H:%M:%S"),
            ]
        )
    if task_conf.penalties.hours:
        penalty_config = ",".join(
            f"{hour}={factor}"
            for hour, factor in zip(
                task_conf.penalties.hours, task_conf.penalties.factors
            )
        )
        args.extend(["--penalty-config", penalty_config])

    stage_conf = result.StageDetail(
        name="teapot",
        executor=result.Executor(
            name="local",
            with_=result.ExecutorWith(
                default=result.Cmd(
                    args=args,
                    env=get_teapot_env(repo_conf),
                    cpu_limit=common.Time("30s"),
                    clock_limit=common.Time("60s"),
                ),
                cases=[],
            ),
        ),
        parsers=[
            result.Parser(name="log", with_=result.MsgConfig(msg="joj3 summary")),
            result.Parser(name="debug"),
        ],
    )
    return stage_conf


def get_check_lists(repo_conf: repo.Config) -> Tuple[List[str], List[str]]:
    base_dir = (repo_conf.root / repo_conf.path).parent
    immutable_dir = base_dir / "immutable_files"
    immutable_files = []
    file_sums = []
    file_paths = []
    for file in repo_conf.files.immutable:
        file_path = immutable_dir / Path(file).name
        if not file_path.exists():
            file_path = immutable_dir / Path(file).name
            logger.warning(f"Immutable file not found: {file_path}")
            if not file_path.exists():
                logger.warning(f"Immutable file not found: {file_path}")
                logger.warning(f"Skipping {file}")
                continue
        immutable_files.append(file_path)
        file_sums.append(calc_sha256sum(file_path))
        file_paths.append(file)
    new_immutable_dir = (
        repo_conf.root / repo_conf.path
    ).parent / repo_conf.health_check.immutable_path
    if not new_immutable_dir.exists():
        file_names = [Path(file).name for file in file_paths]
        for file_path in sorted(immutable_dir.glob("**/*")):
            file_path_name = file_path.name
            if file_path_name not in file_names:
                logger.error(
                    f"Immutable file exists in {immutable_dir}, "
                    f"but not found in health check: {file_path}."
                )
                logger.error(
                    f"Recommnd to move immutable files (keeping nested structure) to {new_immutable_dir}."
                )
                sys.exit(1)
        return file_sums, file_paths
    immutable_dir = new_immutable_dir
    file_sums = []
    file_paths = []
    for file_path in sorted(immutable_dir.glob("**/*")):
        if file_path.is_dir():
            continue
        if not file_path.exists():
            logger.warning(f"Immutable file not found: {file_path}")
            continue
        file_sums.append(calc_sha256sum(file_path))
        file_paths.append(file_path.relative_to(immutable_dir).as_posix())
    return file_sums, file_paths


def get_health_check_args(repo_conf: repo.Config) -> List[str]:
    file_sums, file_paths = get_check_lists(repo_conf)
    return [
        "/usr/local/bin/repo-health-checker",
        "-root=.",
        f"-repoSize={str(repo_conf.health_check.max_size / 1024 / 1024)}",  # B -> MB
        *[f"-meta={meta}" for meta in repo_conf.health_check.required_files],
        f"-checkFileSumList={','.join(file_sums)}",
        f"-checkFileNameList={','.join(file_paths)}",
    ]


def get_teapot_check_args(repo_conf: repo.Config, task_conf: task.Config) -> List[str]:
    res = [
        "/usr/local/bin/joint-teapot",
        "joj3-check-env",
        str(TEAPOT_CONFIG_ROOT / "teapot.env"),
        "--grading-repo-name",
        repo_conf.grading_repo_name,
        "--scoreboard-filename",
        task_conf.scoreboard,
    ]
    if repo_conf.groups.name:
        group_str = lambda groups: ",".join(
            f"{name}={max_count}:{time_period}"
            for name, max_count, time_period in zip(
                groups.name,
                groups.max_count,
                groups.time_period_hour,
            )
        )
        group_config = group_str(
            task_conf.groups if task_conf.groups.name else repo_conf.groups
        )
        res.extend(["--group-config", group_config])
    if task_conf.time.begin:
        res.extend(["--begin-time", task_conf.time.begin.strftime("%Y-%m-%dT%H:%M:%S")])
    if task_conf.time.end:
        res.extend(["--end-time", task_conf.time.end.strftime("%Y-%m-%dT%H:%M:%S")])
    if task_conf.penalties.hours:
        penalty_config = ",".join(
            f"{hour}={factor}"
            for hour, factor in zip(
                task_conf.penalties.hours, task_conf.penalties.factors
            )
        )
        res.extend(["--penalty-config", penalty_config])
    return res


def get_health_check_stage(
    repo_conf: repo.Config, task_conf: task.Config
) -> result.StageDetail:
    health_check_stage = result.StageDetail(
        name="Health Check",
        group="",
        executor=result.Executor(
            name="local",
            with_=result.ExecutorWith(
                default=result.Cmd(
                    cpu_limit=common.Time("10s"),
                    clock_limit=common.Time("20s"),
                ),
                cases=[
                    result.OptionalCmd(
                        args=get_health_check_args(repo_conf),
                    ),
                    result.OptionalCmd(
                        args=get_teapot_check_args(repo_conf, task_conf),
                        env=get_teapot_env(repo_conf),
                    ),
                ],
            ),
        ),
        parsers=[
            result.Parser(
                name="healthcheck",
                with_=result.ScoreConfig(score=repo_conf.health_check.score),
            ),
            result.Parser(name="debug"),
        ],
    )
    return health_check_stage


def calc_sha256sum(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(64 * 1024), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
