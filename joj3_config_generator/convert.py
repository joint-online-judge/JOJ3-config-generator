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


# FIXME: LLM generated convert function, only for demostration
def convert(repo_conf: Repo, task_conf: Task) -> ResultConfig:
    # Create the base ResultConf object
    result_conf = ResultConfig(
        name=task_conf.task,
        log_path=f"{task_conf.task.replace(' ', '_')}.log",
        expire_unix_timestamp=(
            int(task_conf.release.deadline.timestamp())
            if task_conf.release.deadline
            else -1
        ),
        stage=StageConfig(stages=[], sandbox_token=repo_conf.sandbox_token),
        teapot=TeapotConfig(),
    )

    # Convert each stage in the task configuration
    for task_stage in task_conf.stages:
        executor_with_config = ExecutorWithConfig(
            default=Cmd(
                args=task_stage.command.split(),
                copy_in={file: CmdFile(src=file) for file in task_stage.files.import_},
                copy_out_cached=task_stage.files.export,
            ),
            cases=[],  # You can add cases if needed
        )
        conf_stage = Stage(
            name=task_stage.name,
            group=task_conf.task,
            executor=ExecutorConfig(
                name="sandbox",
                with_=executor_with_config,
            ),
            parsers=[
                ParserConfig(name=parser, with_={}) for parser in task_stage.parsers
            ],
        )

        if "result-detail" in task_stage.parsers:
            result_detail_parser = next(
                p for p in conf_stage.parsers if p.name == "result-detail"
            )
            result_detail_parser.with_.update(task_stage.result_detail)

        result_conf.stage.stages.append(conf_stage)

    return result_conf
