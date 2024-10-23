from joj3_config_generator.lib.repo import getHealthcheckConfig, getTeapotConfig
from joj3_config_generator.lib.task import fix_keyword
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
def convert(repo_conf: repo.Config, task_conf: task.Config) -> result.Config:
    # Create the base ResultConf object
    # FIXME: wrap things in functions
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
    cached = []
    # Convert each stage in the task configuration
    for task_stage in task_conf.stages:
        file_import = (
            task_stage.files.import_
            if hasattr(task_stage, "files")
            and hasattr(task_stage.files, "import_")
            and (task_stage.files is not None)
            and (task_stage.files.import_ is not None)
            else []
        )
        copy_in_files = [file for file in file_import if (file not in cached)]
        file_export = (
            task_stage.files.export
            if hasattr(task_stage, "files")
            and hasattr(task_stage.files, "export")
            and (task_stage.files is not None)
            else []
        )
        executor_with_config = ExecutorWithConfig(
            default=Cmd(
                args=task_stage.command.split(),
                copy_in={
                    file: CmdFile(src=f"/home/tt/.config/joj/{file}")
                    for file in copy_in_files
                },
                copy_in_cached={file: file for file in copy_in_files},
                copy_out_cached=file_export if file_export is not None else [],
            ),
            cases=[],  # You can add cases if needed
        )
        if file_export is not None:
            for file in file_export:
                if file not in cached:
                    cached.append(file)
        conf_stage = Stage(
            name=task_stage.name,
            # TODO: we may have cq in future
            group="joj" if "judge" in task_stage.name else None,
            executor=ExecutorConfig(
                name="sandbox",
                with_=executor_with_config,
            ),
            parsers=[
                ParserConfig(name=parser, with_={}) for parser in task_stage.parsers
            ],
        )
        # TODO: fix all parser here
        if "result-detail" in task_stage.parsers:
            result_detail_parser = next(
                p for p in conf_stage.parsers if p.name == "result-detail"
            )
            if task_stage.result_detail is not None:
                result_detail_parser.with_.update(task_stage.result_detail)

        if "dummy" in task_stage.parsers:
            dummy_parser = next(p for p in conf_stage.parsers if p.name == "dummy")
            if task_stage.dummy is not None:
                dummy_parser.with_.update(task_stage.dummy)

        if "result-status" in task_stage.parsers:
            result_status_parser = next(
                p for p in conf_stage.parsers if p.name == "result-status"
            )
            if task_stage.result_status is not None:
                result_status_parser.with_.update(task_stage.result_status)

        conf_stage = fix_keyword(task_stage, conf_stage)

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
        task=joj1_conf.languages[0].language if joj1_conf.languages else "Unnamed Task",
        release=task.Release(deadline=release_deadline),
        stages=stages,
    )
