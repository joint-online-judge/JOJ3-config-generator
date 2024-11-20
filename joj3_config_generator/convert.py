import json
import os
from typing import Any, List

import rtoml

from joj3_config_generator.models import joj1, repo, result, task
from joj3_config_generator.processers.repo import (
    get_healthcheck_config,
    get_teapot_config,
)
from joj3_config_generator.processers.task import (
    fix_diff,
    fix_dummy,
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
        log_path=f"/home/tt/.cache/joj3/{task_conf.task.type_}.log",
        expire_unix_timestamp=(
            int(task_conf.release.deadline.timestamp())
            if task_conf.release.deadline
            else -1
        ),
        stage=result.Stage(stages=[], sandbox_token=repo_conf.sandbox_token),
        teapot=get_teapot_config(repo_conf, task_conf),
    )

    # Construct healthcheck stage
    healthcheck_stage = get_healthcheck_config(repo_conf)
    result_conf.stage.stages.append(healthcheck_stage)
    cached: List[str] = []
    # Convert each stage in the task configuration
    for task_stage in task_conf.stages:
        executor_with_config, cached = get_executorWithConfig(task_stage, cached)
        conf_stage = get_conf_stage(task_stage, executor_with_config)
        conf_stage = fix_result_detail(task_stage, conf_stage)
        conf_stage = fix_dummy(task_stage, conf_stage)
        conf_stage = fix_keyword(task_stage, conf_stage)
        conf_stage = fix_diff(task_stage, conf_stage, task_conf)
        result_conf.stage.stages.append(conf_stage)

    return result_conf


# FIXME: LLM generated convert function, only for demostration
def convert_joj1(joj1_conf: joj1.Config) -> task.Config:
    stages = []
    for language in joj1_conf.languages:
        # Here you might want to create a stage for each language
        # You can define a command based on language properties
        command = f"run {language.language}"
        # Assuming we don't have explicit files, we will set empty ones or default behavior
        files = task.Files(import_=[], export=[])
        # Score can be derived from the first case or set to a default
        score = 0
        parsers: List[str] = []  # Define parsers if applicable
        if joj1_conf.cases:
            score = sum(
                case.score for case in joj1_conf.cases
            )  # Sum scores for all cases
        # Creating a stage for each language
        stages.append(
            task.Stage(
                name=language.language,
                command=command,
                files=files,
                score=score,
                parsers=parsers,
            )
        )
    # Assuming no deadline is provided in `joj1`, you can set it accordingly
    release_deadline = (
        None  # Placeholder for future implementation if deadlines are defined
    )

    return task.Config(
        task=task.Task(
            name=(
                joj1_conf.languages[0].language
                if joj1_conf.languages
                else "Unnamed Task"
            ),
            type_="",
        ),  # FIXME: fix this type later
        release=task.Release(deadline=release_deadline),
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
    return 0
