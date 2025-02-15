import json
import os
from pathlib import Path
from typing import Any, List

import rtoml

from joj3_config_generator.models import joj1, repo, result, task
from joj3_config_generator.processers.joj1 import get_joj1_run_stage
from joj3_config_generator.processers.repo import (  # get_teapotcheck_config,
    get_healthcheck_config,
    get_teapot_stage,
)
from joj3_config_generator.processers.task import (
    fix_diff,
    fix_dummy,
    fix_file,
    fix_keyword,
    fix_result_detail,
    get_conf_stage,
    get_executorWithConfig,
)


def convert(repo_conf: repo.Config, task_conf: task.Config) -> result.Config:
    # Create the base ResultConf object
    result_conf = result.Config(
        name=task_conf.task.name,
        # TODO: specify the exact folder difference
        log_path=f"{Path.home()}/.cache/joj3/{task_conf.task.type_}.log",
        expire_unix_timestamp=(
            int(task_conf.release.deadline.timestamp())
            if task_conf.release.deadline
            else -1
        ),
        # FIXME: don't hardcode
        actor_csv_path=f"{Path.home()}/.config/joj/students.csv",
        stage=result.Stage(
            stages=[],
            sandbox_token=repo_conf.sandbox_token,
            poststages=[get_teapot_stage(repo_conf)],
        ),
    )

    # Construct healthcheck stage
    healthcheck_stage = get_healthcheck_config(repo_conf)
    # teapotcheck_stage = get_teapotcheck_config(repo_conf, task_conf)
    result_conf.stage.stages.append(healthcheck_stage)
    cached: List[str] = []
    # Convert each stage in the task configuration
    for task_stage in task_conf.stages:
        executor_with_config, cached = get_executorWithConfig(task_stage, cached)
        conf_stage = get_conf_stage(task_stage, executor_with_config)
        conf_stage = fix_result_detail(task_stage, conf_stage)
        conf_stage = fix_dummy(task_stage, conf_stage)
        conf_stage = fix_keyword(task_stage, conf_stage)
        conf_stage = fix_file(task_stage, conf_stage)
        conf_stage = fix_diff(task_stage, conf_stage, task_conf)
        result_conf.stage.stages.append(conf_stage)

    return result_conf


def convert_joj1(joj1_conf: joj1.Config) -> task.Config:
    stages = [get_joj1_run_stage(joj1_conf)]
    return task.Config(
        task=task.Task(
            name=("Blank Task"),
        ),
        release=task.Release(deadline=None),
        stages=stages,
    )


def distribute_json(folder_path: str, repo_obj: Any) -> None:
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".toml"):
                toml_file_path = os.path.join(root, file)
                json_file_path = os.path.join(root, file.replace(".toml", ".json"))
                with open(toml_file_path) as toml_file:
                    task_toml = toml_file.read()
                task_obj = rtoml.loads(task_toml)
                result_model = convert(repo.Config(**repo_obj), task.Config(**task_obj))
                result_dict = result_model.model_dump(by_alias=True, exclude_none=True)

                with open(json_file_path, "w") as result_file:
                    json.dump(result_dict, result_file, ensure_ascii=False, indent=4)
                    result_file.write("\n")
                    print(f"Successfully convert {toml_file_path} into json!")
                    assert os.path.exists(
                        json_file_path
                    ), f"Failed to convert {toml_file_path} into json!"
