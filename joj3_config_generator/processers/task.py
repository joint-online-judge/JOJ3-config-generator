import re
import shlex
from typing import List, Tuple

from joj3_config_generator.models import result, task


def get_conf_stage(
    task_stage: task.Stage, executor_with_config: result.ExecutorWith
) -> result.StageDetail:
    conf_stage = result.StageDetail(
        name=task_stage.name if task_stage.name is not None else "",
        # group is determined by adding between "[]" in the name of the task
        # FIXME: this is probably outdated
        group=(
            match.group(1)
            if (match := re.search(r"\[([^\[\]]+)\]", task_stage.name or ""))
            else ""
        ),
        executor=result.Executor(
            name="sandbox",
            with_=executor_with_config,
        ),
        parsers=(
            [
                result.ParserConfig(name=parser, with_={})
                for parser in task_stage.parsers
            ]
            if task_stage.parsers is not None
            else []
        ),
    )
    return conf_stage


def get_executor_with_config(
    task_stage: task.Stage, cached: List[str]
) -> Tuple[result.ExecutorWith, List[str]]:
    file_import = (
        task_stage.files.import_
        if hasattr(task_stage, "files")
        and hasattr(task_stage.files, "import_")
        and (task_stage.files is not None)
        and (task_stage.files.import_ is not None)
        else []
    )
    copy_in_files = [file for file in file_import if file not in cached]
    file_export = (
        task_stage.files.export
        if hasattr(task_stage, "files")
        and hasattr(task_stage.files, "export")
        and (task_stage.files is not None)
        else []
    )
    copy_out_files = ["stdout", "stderr"]
    executor_with_config = result.ExecutorWith(
        default=result.Cmd(
            args=(
                shlex.split(task_stage.command)
                if task_stage.command is not None
                else []
            ),
            copy_in={
                file: result.LocalFile(src=f"/home/tt/.config/joj/{file}")
                # all copyin files store in this tools folder
                # are there any corner cases
                for file in copy_in_files
            },
            copy_out=copy_out_files,
            copy_in_cached={file: file for file in cached},
            copy_out_cached=file_export or [],
            cpu_limit=task_stage.limit.cpu,
            clock_limit=2 * task_stage.limit.cpu,
            memory_limit=task_stage.limit.mem,
            stderr=result.Collector(name="stderr"),
            stdout=result.Collector(name="stdout"),
        ),
        cases=[],
    )
    if file_export is not None:
        for file in file_export:
            if file not in cached:
                cached.append(file)
    return (executor_with_config, cached)


def fix_keyword(
    task_stage: task.Stage, conf_stage: result.StageDetail
) -> result.StageDetail:
    keyword_parser = ["clangtidy", "keyword", "cppcheck", "cpplint"]
    for parser in task_stage.parsers or []:
        if parser in keyword_parser:
            keyword_parser_ = next(p for p in conf_stage.parsers if p.name == parser)
            keyword_weight = []
            if getattr(task_stage, parser, None) is not None:
                unique_weight = list(set(getattr(task_stage, parser).weight))
                for score in unique_weight:
                    keyword_weight.append({"keywords": [], "score": score})

                for idx, score in enumerate(unique_weight):
                    for idx_, score_ in enumerate(getattr(task_stage, parser).weight):
                        if score == score_:
                            keyword_weight[idx]["keywords"].append(
                                getattr(task_stage, parser).keyword[idx_]
                            )
                        else:
                            continue
            else:
                continue

            keyword_parser_.with_.update(
                {
                    "matches": keyword_weight,
                }
            )
    return conf_stage


def fix_result_detail(
    task_stage: task.Stage, conf_stage: result.StageDetail
) -> result.StageDetail:
    if (task_stage.parsers is not None) and ("result-detail" in task_stage.parsers):
        result_detail_parser = next(
            p for p in conf_stage.parsers if p.name == "result-detail"
        )
        if task_stage.result_detail is not None:
            show_files = []
            if task_stage.result_detail.stdout:
                show_files.append("stdout")
            if task_stage.result_detail.stderr:
                show_files.append("stderr")
            result_detail_parser.with_.update(
                result.ResultDetailConfig(
                    score=0,
                    comment="",
                    show_files=show_files,
                    show_exit_status=task_stage.result_detail.exitstatus,
                    show_runtime=task_stage.result_detail.time,
                    show_memory=task_stage.result_detail.mem,
                ).model_dump(by_alias=True)
            )

    return conf_stage


def fix_dummy(
    task_stage: task.Stage, conf_stage: result.StageDetail
) -> result.StageDetail:
    dummy_parser = [
        "dummy",
        "result-status",
    ]
    if task_stage.parsers is not None:
        for parser in task_stage.parsers:
            if parser not in dummy_parser:
                continue
            dummy_parser_ = next(p for p in conf_stage.parsers if p.name == parser)
            if getattr(task_stage, parser.replace("-", "_"), None) is None:
                continue
            if task_stage.result_status is None:
                continue
            dummy_parser_.with_.update(
                result.DummyConfig(
                    score=task_stage.result_status.score,
                    comment=task_stage.result_status.comment,
                    force_quit_on_not_accepted=task_stage.result_status.forcequit,
                ).model_dump(by_alias=True)
            )
    return conf_stage


def fix_file(
    task_stage: task.Stage, conf_stage: result.StageDetail
) -> result.StageDetail:
    file_parser = ["file"]
    if task_stage.parsers is not None:
        for parser in task_stage.parsers:
            if parser in file_parser:
                file_parser_ = next(p for p in conf_stage.parsers if p.name == parser)
                if task_stage.file is not None:
                    file_parser_.with_.update({"name": task_stage.file.name})
            else:
                continue
    return conf_stage


def fix_diff(
    task_stage: task.Stage,
    conf_stage: result.StageDetail,
    task_conf: task.Config,
) -> result.StageDetail:
    if task_stage.parsers is not None and "diff" in task_stage.parsers:
        diff_parser = next((p for p in conf_stage.parsers if p.name == "diff"), None)
        skip = task_stage.skip or []
        cases = task_stage.cases or {}
        finalized_cases = [case for case in cases if case not in skip]

        stage_cases = []
        parser_cases = []

        for case in finalized_cases:
            case_stage = task_stage.cases.get(case) if task_stage.cases else None
            if not case_stage:
                continue

            cpu_limit = case_stage.limit.cpu
            clock_limit = 2 * case_stage.limit.cpu
            memory_limit = case_stage.limit.mem
            command = case_stage.command if case_stage.command is not None else None
            stdin = case_stage.in_ if case_stage.in_ != "" else f"{case}.in"
            stdout = case_stage.out_ if case_stage.out_ != "" else f"{case}.out"

            stage_cases.append(
                result.OptionalCmd(
                    stdin=result.LocalFile(
                        src=f"/home/tt/.config/joj/{task_conf.task.type_}/{stdin}",
                    ),
                    args=(shlex.split(command) if command is not None else None),
                    cpu_limit=cpu_limit,
                    clock_limit=clock_limit,
                    memory_limit=memory_limit,
                    proc_limit=50,
                )
            )

            # Ensure case_stage.diff and case_stage.diff.output are defined
            diff_output = (
                case_stage.diff.output
                if case_stage.diff and case_stage.diff.output
                else None
            )
            if diff_output:
                parser_cases.append(
                    {
                        "outputs": [
                            result.DiffOutputConfig(
                                score=diff_output.score,
                                file_name="stdout",
                                answer_path=f"/home/tt/.config/joj/{task_conf.task.type_}/{stdout}",
                                force_quit_on_diff=diff_output.forcequit,
                                always_hide=diff_output.hide,
                                compare_space=not diff_output.ignorespaces,
                            ).model_dump(by_alias=True)
                        ]
                    }
                )

        if diff_parser and task_stage.diff is not None:
            diff_parser.with_.update({"name": "diff", "cases": parser_cases})
            conf_stage.executor.with_.cases = stage_cases

    return conf_stage
