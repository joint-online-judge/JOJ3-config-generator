import hashlib
from pathlib import Path
from typing import List

from joj3_config_generator.models import common, repo, result, task
from joj3_config_generator.models.const import (
    CACHE_ROOT,
    TEAPOT_CONFIG_ROOT,
    TEAPOT_LOG_PATH,
)


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
            str(repo_conf.max_total_score)
            if not task_conf.max_total_score
            else str(task_conf.max_total_score)
        ),
    ]
    if not repo_conf.submitter_in_issue_title:
        args.append("--no-submitter-in-issue-title")

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


def get_health_check_args(repo_conf: repo.Config) -> List[str]:
    return [
        "/usr/local/bin/repo-health-checker",
        "-root=.",
        f"-repoSize={str(repo_conf.max_size)}",
        *[f"-meta={meta}" for meta in repo_conf.files.required],
        f"-checkFileSumList={','.join(get_hashes(repo_conf))}",
        f"-checkFileNameList={','.join(repo_conf.files.immutable)}",
    ]


def get_teapot_check_args(repo_conf: repo.Config, task_conf: task.Config) -> List[str]:
    res = [
        "/usr/local/bin/joint-teapot",
        "joj3-check-env",
        str(TEAPOT_CONFIG_ROOT / "teapot.env"),
        "--grading-repo-name",
        repo_conf.grading_repo_name,
    ]
    if repo_conf.groups.name:
        group_config_str = ",".join(
            f"{name}={max_count}:{time_period}"
            for name, max_count, time_period in zip(
                repo_conf.groups.name,
                repo_conf.groups.max_count,
                repo_conf.groups.time_period_hour,
            )
        )
        if task_conf.groups.name:
            overwrite_group_config_str = ",".join(
                f"{name}={max_count}:{time_period}"
                for name, max_count, time_period in zip(
                    task_conf.groups.name,
                    task_conf.groups.max_count,
                    task_conf.groups.time_period_hour,
                )
            )
            res.extend(["--group-config", overwrite_group_config_str])
        else:
            res.extend(["--group-config", group_config_str])
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
                    cpu_limit=common.Time("10s"), clock_limit=common.Time("20s")
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
                with_=result.ScoreConfig(score=repo_conf.health_check_score),
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


def get_hashes(repo_conf: repo.Config) -> List[str]:
    base_dir = (repo_conf.root / repo_conf.path).parent
    immutable_dir = base_dir / "immutable_files"
    immutable_files = [
        immutable_dir / Path(file).name for file in repo_conf.files.immutable
    ]
    return [calc_sha256sum(file) for file in immutable_files]
