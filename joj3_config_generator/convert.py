import os
from typing import Dict

from joj3_config_generator.models import joj1, repo, result, task
from joj3_config_generator.models.const import CACHE_ROOT, JOJ3_CONFIG_ROOT
from joj3_config_generator.processers.repo import (
    get_health_check_stage,
    get_teapot_stage,
)
from joj3_config_generator.processers.task import get_conf_stage


def convert(repo_conf: repo.Config, task_conf: task.Config) -> result.Config:
    # Create the base ResultConf object
    result_conf = result.Config(
        name=task_conf.task.name,
        # exact folder difference specified by type
        log_path=str(CACHE_ROOT / "joj3" / f"{task_conf.task.type_}.log"),
        expire_unix_timestamp=int(task_conf.release.end_time.timestamp()),
        effective_unix_timestamp=int(task_conf.release.begin_time.timestamp()),
        actor_csv_path=str(JOJ3_CONFIG_ROOT / "students.csv"),  # students.csv position
        max_total_score=repo_conf.max_total_score,
        stage=result.Stage(sandbox_token=repo_conf.sandbox_token),
    )

    current_test = os.environ.get("PYTEST_CURRENT_TEST") is not None
    # Construct health check stage
    if not repo_conf.force_skip_health_check_on_test or not current_test:
        result_conf.stage.stages.append(get_health_check_stage(repo_conf))
    cached: Dict[str, None] = {}
    # Convert each stage in the task configuration
    for task_stage in task_conf.stages:
        result_conf.stage.stages.append(get_conf_stage(task_conf, task_stage, cached))
    if not repo_conf.force_skip_teapot_on_test or not current_test:
        result_conf.stage.post_stages.append(get_teapot_stage(repo_conf))

    return result_conf


def convert_joj1(joj1_conf: joj1.Config) -> task.Config:
    return task.Config()
