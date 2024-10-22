from joj3_config_generator.models import joj1, repo, result, task


# FIXME: LLM generated convert function, only for demostration
def convert(repo_conf: repo.Config, task_conf: task.Config) -> result.Config:
    # Create the base ResultConf object
    result_conf = result.Config(
        name=task_conf.task,
        log_path=f"{task_conf.task.replace(' ', '_')}.log",
        expire_unix_timestamp=(
            int(task_conf.release.deadline.timestamp())
            if task_conf.release.deadline
            else -1
        ),
        stage=result.Stage(stages=[], sandbox_token=repo_conf.sandbox_token),
        teapot=result.Teapot(),
    )

    # Convert each stage in the task configuration
    for task_stage in task_conf.stages:
        executor_with_config = result.ExecutorWith(
            default=result.Cmd(
                args=task_stage.command.split(),
                copy_in={
                    file: result.CmdFile(src=file) for file in task_stage.files.import_
                },
                copy_out_cached=task_stage.files.export,
            ),
            cases=[],  # You can add cases if needed
        )
        conf_stage = result.StageDetail(
            name=task_stage.name,
            group=task_conf.task,
            executor=result.Executor(
                name="sandbox",
                with_=executor_with_config,
            ),
            parsers=[
                result.Parser(name=parser, with_={}) for parser in task_stage.parsers
            ],
        )

        if "result-detail" in task_stage.parsers:
            result_detail_parser = next(
                p for p in conf_stage.parsers if p.name == "result-detail"
            )
            result_detail_parser.with_.update(task_stage.result_detail)

        result_conf.stage.stages.append(conf_stage)

    return result_conf


# TODO: implement me
def convert_joj1(joj1_conf: joj1.Config) -> task.Config:
    return task.Config(task="", release=task.Release(deadline=None), stages=[])
