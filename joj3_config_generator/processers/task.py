import re
import shlex
from typing import Any, Callable, Dict, List, Tuple

from joj3_config_generator.models import result, task
from joj3_config_generator.models.const import JOJ3_CONFIG_ROOT


def get_conf_stage(
    task_conf: task.Config,
    task_stage: task.Stage,
    cached: Dict[str, None],
) -> result.StageDetail:
    conf_stage = result.StageDetail(
        name=task_stage.name,
        # group is determined by adding between "[]" in the name of the task
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
            [result.Parser(name=parser, with_={}) for parser in task_stage.parsers]
        ),
    )
    processed_dict = get_processed_dict(task_stage)
    for idx, parser in enumerate(task_stage.parsers):
        if parser in processed_dict or parser.replace("-", "_") in processed_dict:
            fn, parser_model = processed_dict[parser]
            fn(parser_model, conf_stage.parsers[idx])
        elif parser == "diff":
            fix_diff(task_stage, task_conf, conf_stage.parsers[idx], conf_stage)
        else:
            continue
    return conf_stage


def get_processed_dict(
    task_stage: task.Stage,
) -> Dict[str, Tuple[Callable[[Any, result.Parser], None], Any]]:
    processed_dict: Dict[str, Tuple[Callable[[Any, result.Parser], None], Any]] = {
        "clangtidy": (fix_keyword, task_stage.clangtidy),
        "keyword": (fix_keyword, task_stage.keyword),
        "cppcheck": (fix_keyword, task_stage.cppcheck),
        "cpplint": (fix_keyword, task_stage.cpplint),
        "result-detail": (fix_result_detail, task_stage.result_detail),
        "dummy": (fix_dummy, task_stage.dummy),
        "result-status": (fix_dummy, task_stage.result_status),
        "file": (fix_file, task_stage.file),
    }
    return processed_dict


def get_executor_with(
    task_stage: task.Stage, cached: Dict[str, None]
) -> result.ExecutorWith:
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
        cached[file] = None
    return executor_with_config


def fix_keyword(
    keyword_config: task.ParserKeyword, keyword_parser_: result.Parser
) -> None:
    keyword_weight: List[result.KeywordConfig] = []
    unique_weight = list(set(keyword_config.weight))
    for score in unique_weight:
        keyword_weight.append(result.KeywordConfig(keywords=[], score=score))

    for idx, score in enumerate(unique_weight):
        for idx_, score_ in enumerate(keyword_config.weight):
            if score == score_:
                keyword_weight[idx].keywords.append(keyword_config.keyword[idx_])
            else:
                continue

    keyword_parser_.with_.update(
        result.KeywordMatchConfig(
            matches=keyword_weight,
        ).model_dump(by_alias=True)
    )


def fix_result_detail(
    result_detail_parser_config: task.ParserResultDetail,
    result_detail_parser: result.Parser,
) -> None:
    show_files = []
    if result_detail_parser_config.stdout:
        show_files.append("stdout")
    if result_detail_parser_config.stderr:
        show_files.append("stderr")
    result_detail_parser.with_.update(
        result.ResultDetailConfig(
            score=0,
            comment="",
            show_files=show_files,
            show_exit_status=result_detail_parser_config.exitstatus,
            show_runtime=result_detail_parser_config.time,
            show_memory=result_detail_parser_config.mem,
        ).model_dump(by_alias=True)
    )


def fix_dummy(
    dummy_parser_config: task.ParserDummy, dummy_parser: result.Parser
) -> None:
    # we don't use dummy parser in real application
    if dummy_parser_config is None:
        return
    dummy_parser.with_.update(
        result.DummyConfig(
            score=dummy_parser_config.score,
            comment=dummy_parser_config.comment,
            force_quit_on_not_accepted=dummy_parser_config.force_quit,
        ).model_dump(by_alias=True)
    )
    return


def fix_file(file_parser_config: task.ParserFile, file_parser: result.Parser) -> None:
    file_parser.with_.update(
        result.FileConfig(name=file_parser_config.name).model_dump(by_alias=True)
    )


def fix_diff(
    task_stage: task.Stage,
    task_conf: task.Config,
    diff_parser_config: result.Parser,
    conf_stage: result.StageDetail,
) -> None:
    diff_parser = diff_parser_config
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
                    src=str(JOJ3_CONFIG_ROOT / task_conf.path.parent / stdin),
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
                result.DiffCasesConfig(
                    outputs=[
                        result.DiffOutputConfig(
                            score=diff_output.score,
                            file_name="stdout",
                            answer_path=str(
                                JOJ3_CONFIG_ROOT / task_conf.path.parent / stdout
                            ),
                            force_quit_on_diff=diff_output.force_quit,
                            always_hide=diff_output.hide,
                            compare_space=not diff_output.ignore_spaces,
                        )
                    ]
                )
            )

    if diff_parser:
        diff_parser.with_.update(
            result.DiffConfig(name="diff", cases=parser_cases).model_dump(by_alias=True)
        )
        conf_stage.executor.with_.cases = stage_cases

    return
