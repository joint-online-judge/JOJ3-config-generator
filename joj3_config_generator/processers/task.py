import re
import shlex
from typing import Set

from joj3_config_generator.models import result, task
from joj3_config_generator.models.const import JOJ3_CONFIG_ROOT


def get_conf_stage(
    task_conf: task.Config,
    task_stage: task.Stage,
    cached: Set[str],
) -> result.StageDetail:
    conf_stage = result.StageDetail(
        name=task_stage.name,
        # group is determined by adding between "[]" in the name of the task
        # FIXME: this is probably outdated
        group=(
            match.group(1)
            if (match := re.search(r"\[([^\[\]]+)\]", task_stage.name or ""))
            else ""
        ),
        executor=result.Executor(
            name="sandbox",
            with_=get_executor_with(task_stage, cached),
        ),
        parsers=(
            [
                result.ParserConfig(name=parser, with_={})
                for parser in task_stage.parsers
            ]
        ),
    )
    fix_result_detail(task_stage, conf_stage)
    fix_dummy(task_stage, conf_stage)
    fix_keyword(task_stage, conf_stage)
    fix_file(task_stage, conf_stage)
    fix_diff(task_stage, task_conf, conf_stage)
    return conf_stage


def get_executor_with(task_stage: task.Stage, cached: Set[str]) -> result.ExecutorWith:
    file_import = task_stage.files.import_
    copy_in_files = [file for file in file_import if file not in cached]
    file_export = task_stage.files.export
    copy_out_files = ["stdout", "stderr"]
    executor_with_config = result.ExecutorWith(
        default=result.Cmd(
            args=shlex.split(task_stage.command),
            copy_in={
                file: result.LocalFile(src=str(JOJ3_CONFIG_ROOT / file))
                # all copyin files store in this tools folder
                # are there any corner cases
                for file in copy_in_files
            },
            copy_out=copy_out_files,
            copy_in_cached={file: file for file in cached},
            copy_out_cached=file_export,
            cpu_limit=task_stage.limit.cpu,
            clock_limit=2 * task_stage.limit.cpu,
            memory_limit=task_stage.limit.mem,
            stderr=result.Collector(name="stderr"),
            stdout=result.Collector(name="stdout"),
        ),
        cases=[],
    )
    for file in file_export:
        if file not in cached:
            cached.add(file)
    return executor_with_config


def fix_keyword(
    task_stage: task.Stage, conf_stage: result.StageDetail
) -> result.StageDetail:
    keyword_parser = ["clangtidy", "keyword", "cppcheck", "cpplint"]
    for parser in task_stage.parsers:
        if parser in keyword_parser:
            keyword_parser_ = next(p for p in conf_stage.parsers if p.name == parser)
            keyword_weight = []
            if parser in task_stage.__dict__:
                unique_weight = list(set(task_stage.__dict__[parser].weight))
                for score in unique_weight:
                    keyword_weight.append({"keywords": [], "score": score})

                for idx, score in enumerate(unique_weight):
                    for idx_, score_ in enumerate(task_stage.__dict__[parser].weight):
                        if score == score_:
                            keyword_weight[idx]["keywords"].append(
                                task_stage.__dict__[parser].keyword[idx_]
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


def fix_result_detail(task_stage: task.Stage, conf_stage: result.StageDetail) -> None:
    if "result-detail" not in task_stage.parsers:
        return
    result_detail_parser = next(
        p for p in conf_stage.parsers if p.name == "result-detail"
    )
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


def fix_dummy(task_stage: task.Stage, conf_stage: result.StageDetail) -> None:
    dummy_parser = [
        "dummy",
        "result-status",
    ]
    for parser in task_stage.parsers:
        if parser not in dummy_parser:
            continue
        dummy_parser_ = next(p for p in conf_stage.parsers if p.name == parser)
        if parser.replace("-", "_") not in task_stage.__dict__:
            continue
        if task_stage.result_status is None:
            continue
        dummy_parser_.with_.update(
            result.DummyConfig(
                score=task_stage.result_status.score,
                comment=task_stage.result_status.comment,
                force_quit_on_not_accepted=task_stage.result_status.force_quit,
            ).model_dump(by_alias=True)
        )
    return


def fix_file(task_stage: task.Stage, conf_stage: result.StageDetail) -> None:
    file_parser = ["file"]
    for parser in task_stage.parsers:
        if parser not in file_parser:
            continue
        file_parser_ = next(p for p in conf_stage.parsers if p.name == parser)
        file_parser_.with_.update({"name": task_stage.file.name})


def fix_diff(
    task_stage: task.Stage,
    task_conf: task.Config,
    conf_stage: result.StageDetail,
) -> None:
    if "diff" not in task_stage.parsers:
        return
    diff_parser = next((p for p in conf_stage.parsers if p.name == "diff"), None)
    skip = task_stage.skip
    cases = task_stage.cases
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
        command = case_stage.command
        stdin = case_stage.in_ if case_stage.in_ != "" else f"{case}.in"
        stdout = case_stage.out_ if case_stage.out_ != "" else f"{case}.out"

        stage_cases.append(
            result.OptionalCmd(
                stdin=result.LocalFile(
                    src=str(JOJ3_CONFIG_ROOT / task_conf.task.type_ / stdin),
                ),
                args=shlex.split(command) if command else None,
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
                            answer_path=str(
                                JOJ3_CONFIG_ROOT / task_conf.task.type_ / stdout
                            ),
                            force_quit_on_diff=diff_output.force_quit,
                            always_hide=diff_output.hide,
                            compare_space=not diff_output.ignore_spaces,
                        ).model_dump(by_alias=True)
                    ]
                }
            )

    if diff_parser:
        diff_parser.with_.update({"name": "diff", "cases": parser_cases})
        conf_stage.executor.with_.cases = stage_cases

    return
