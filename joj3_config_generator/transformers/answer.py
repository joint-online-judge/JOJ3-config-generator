from typing import Any, Callable, Dict, List, Type

import tomli

from joj3_config_generator.models import answer, task


def get_task_conf_from_answers(answers: answer.Answers) -> task.Config:
    if answers.template_file_content:
        toml_dict = tomli.loads(answers.template_file_content)
        return task.Config(
            task=task.Task(name=answers.name),
            stages=toml_dict["stages"],
        )
    language = answers.language
    transformer_dict = get_transformer_dict()
    transformer = transformer_dict[type(language)]
    stages = transformer(language)
    return task.Config(task=task.Task(name=answers.name), stages=stages)


def get_transformer_dict() -> Dict[
    Type[Any],
    Callable[[Any], List[task.Stage]],
]:
    return {
        answer.Cpp: get_cpp_stages,
        answer.Python: get_python_stages,
        answer.Rust: get_rust_stages,
    }


# TODO: implement
def get_cpp_stages(language: answer.Cpp) -> List[task.Stage]:
    stages = language.stages
    attribute: answer.Cpp.Attribute = language.attribute
    task_stages = []
    if answer.Cpp.Stage.CPPCHECK in stages:
        task_stages.append(task.Stage(name=answer.Cpp.Stage.CPPCHECK))
    if answer.Cpp.Stage.CPPLINT in stages:
        task_stages.append(task.Stage(name=answer.Cpp.Stage.CPPLINT))
    if answer.Cpp.Stage.CLANG_TIDY in stages:
        task_stages.append(task.Stage(name=answer.Cpp.Stage.CLANG_TIDY))
    if answer.Cpp.Stage.RUN in stages:
        task_stages.append(task.Stage(name=answer.Cpp.Stage.RUN))
    return task_stages


# TODO: implement
def get_python_stages(language: answer.Python) -> List[task.Stage]:
    stages = language.stages
    attribute: answer.Python.Attribute = language.attribute
    return []


# TODO: implement
def get_rust_stages(language: answer.Rust) -> List[task.Stage]:
    stages = language.stages
    attribute: answer.Rust.Attribute = language.attribute
    return []
