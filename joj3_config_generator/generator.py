import os
from typing import Dict

from joj3_config_generator.models import answer, common, joj1, repo, result, task
from joj3_config_generator.models.const import (
    ACTOR_CSV_PATH,
    JOJ3_LOG_BASE_PATH,
    JOJ3_LOG_FILENAME,
    TEAPOT_CONFIG_ROOT,
)
from joj3_config_generator.transformers.answer import get_task_conf_from_answers
from joj3_config_generator.transformers.joj1 import get_task_conf_from_joj1
from joj3_config_generator.transformers.repo import (
    get_health_check_stage,
    get_teapot_env,
    get_teapot_post_stage,
)
from joj3_config_generator.transformers.task import get_conf_stage


def create_joj3_task_conf(answers: answer.Answers) -> task.Config:
    return get_task_conf_from_answers(answers)


def convert_joj1_conf(joj1_conf: joj1.Config) -> task.Config:
    return get_task_conf_from_joj1(joj1_conf)


def convert_joj3_conf(repo_conf: repo.Config, task_conf: task.Config) -> result.Config:
    # Create the base ResultConf object
    result_conf = result.Config(
        name=task_conf.name,
        # exact folder difference specified by type
        log_path=str(JOJ3_LOG_BASE_PATH / task_conf.suffix / JOJ3_LOG_FILENAME),
        actor_csv_path=str(ACTOR_CSV_PATH),  # students.csv position
        sandbox_token=repo_conf.sandbox_token,
    )

    current_test = os.environ.get("PYTEST_CURRENT_TEST") is not None
    # Construct health check stage
    if not repo_conf.force_skip_health_check_on_test or not current_test:
        result_conf.stages.append(get_health_check_stage(repo_conf, task_conf))
    cached: Dict[str, None] = {}
    # Convert each stage in the task configuration
    for task_stage in task_conf.stages:
        result_conf.stages.append(get_conf_stage(task_conf, task_stage, cached))
    if not repo_conf.force_skip_teapot_on_test or not current_test:
        result_conf.post_stages.append(get_teapot_post_stage(repo_conf, task_conf))

    return result_conf


def create_joj3_convert_failure_conf() -> result.Config:
    result_conf = result.Config(
        name="Config generation failure",
        log_path=str(JOJ3_LOG_BASE_PATH / JOJ3_LOG_FILENAME),
    )
    result_conf.stages.append(
        result.StageDetail(
            name="Error Message",
            executor=result.Executor(name="dummy"),
            parsers=[
                result.Parser(
                    name="dummy",
                    with_=result.DummyConfig(
                        comment="Config generation failure. Contact teaching team to check course-joj repo actions for details.",
                        force_quit=True,
                    ),
                )
            ],
        )
    )
    result_conf.post_stages.append(
        result.StageDetail(
            name="teapot",
            executor=result.Executor(
                name="local",
                with_=result.ExecutorWith(
                    default=result.Cmd(
                        args=[
                            "/usr/local/bin/joint-teapot",
                            "joj3-all-env",
                            str(TEAPOT_CONFIG_ROOT / "teapot.env"),
                            "--skip-scoreboard",
                            "--skip-failed-table",
                        ],
                        env=get_teapot_env(),
                        cpu_limit=common.Time("30s"),
                        clock_limit=common.Time("60s"),
                    ),
                    cases=[],
                ),
            ),
            parsers=[
                result.Parser(
                    name="log",
                    with_=result.MsgConfig(
                        filename="stderr",
                        msg="joint-teapot stderr",
                        level=0,
                    ),
                ),
                result.Parser(name="debug"),
            ],
        )
    )
    return result_conf
