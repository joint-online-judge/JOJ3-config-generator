from joj3_config_generator.lib.repo import getHealthcheckConfig, getTeapotConfig
from joj3_config_generator.lib.task import (
    fix_comment,
    fix_diff,
    fix_keyword,
    fix_result_detail,
    get_conf_stage,
    get_executorWithConfig,
)
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


def convert(repo_conf: Repo, task_conf: Task) -> ResultConfig:
    # Create the base ResultConf object
    result_conf = ResultConfig(
        name=task_conf.task,
        # TODO: specify the exact folder difference
        log_path=f"{task_conf.task.replace(' ', '-')}.log",
        expire_unix_timestamp=(
            int(task_conf.release.deadline.timestamp())
            if task_conf.release.deadline
            else -1
        ),
        stage=StageConfig(stages=[], sandbox_token=repo_conf.sandbox_token),
        teapot=getTeapotConfig(repo_conf, task_conf),
    )

    # Construct healthcheck stage
    healthcheck_stage = getHealthcheckConfig(repo_conf, task_conf)
    result_conf.stage.stages.append(healthcheck_stage)
    cached: list[str] = []
    # Convert each stage in the task configuration
    for task_stage in task_conf.stages:
        executor_with_config, cached = get_executorWithConfig(task_stage, cached)
        conf_stage = get_conf_stage(task_stage, executor_with_config)
        conf_stage = fix_result_detail(task_stage, conf_stage)
        conf_stage = fix_comment(task_stage, conf_stage)
        conf_stage = fix_keyword(task_stage, conf_stage)
        conf_stage = fix_diff(task_stage, conf_stage)
        result_conf.stage.stages.append(conf_stage)

    return result_conf
