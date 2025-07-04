import re
import shlex
from functools import partial
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from joj3_config_generator.models import result, task
from joj3_config_generator.models.const import DEFAULT_PATH_ENV, JOJ3_CONFIG_ROOT
from joj3_config_generator.utils.logger import logger


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
        parsers=([result.Parser(name=parser) for parser in task_stage.parsers]),
    )
    parser_handler_map = get_parser_handler_map(
        task_stage,
        conf_stage.executor,
        task_conf.root,
        task_conf.path,
    )
    for idx, parser in enumerate(task_stage.parsers):
        if parser not in parser_handler_map:
            raise ValueError(f"Unknown parser {parser}")
        fn, parser_model = parser_handler_map[parser]
        fn(parser_model, conf_stage.parsers[idx])
    return conf_stage


def get_parser_handler_map(
    task_stage: task.Stage,
    executor: result.Executor,
    task_root: Path,
    task_path: Path,
) -> Dict[task.Parser, Tuple[Callable[[Any, result.Parser], None], Any]]:
    return {
        task.Parser.ELF: (fix_keyword, task_stage.elf),
        task.Parser.CLANG_TIDY: (fix_keyword, task_stage.clangtidy),
        task.Parser.KEYWORD: (fix_keyword, task_stage.keyword),
        task.Parser.CPPCHECK: (fix_keyword, task_stage.cppcheck),
        task.Parser.CPPLINT: (fix_keyword, task_stage.cpplint),
        task.Parser.RESULT_DETAIL: (fix_result_detail, task_stage.result_detail),
        task.Parser.DUMMY: (fix_dummy, task_stage.dummy),
        task.Parser.RESULT_STATUS: (fix_result_status, task_stage.result_status),
        task.Parser.FILE: (fix_file, task_stage.file),
        task.Parser.DIFF: (
            partial(
                fix_diff,
                task_stage=task_stage,
                executor=executor,
                task_root=task_root,
                task_path=task_path,
            ),
            task_stage.diff,
        ),
    }


def get_executor_with(
    task_stage: task.Stage, cached: Dict[str, None]
) -> result.ExecutorWith:
    copy_in: dict[
        str,
        Union[result.LocalFile, result.MemoryFile, result.PreparedFile, result.Symlink],
    ] = {
        file: result.LocalFile(src=str(JOJ3_CONFIG_ROOT / file))
        for file in task_stage.files.import_
        if file not in cached
    }
    for src, dst in task_stage.files.import_map.items():
        if dst in cached:
            continue
        copy_in[dst] = result.LocalFile(src=str(JOJ3_CONFIG_ROOT / src))
    file_export = task_stage.files.export
    copy_out_files = ["stdout", "stderr"]
    executor_with_config = result.ExecutorWith(
        default=result.Cmd(
            args=shlex.split(task_stage.command),
            env=[DEFAULT_PATH_ENV, *task_stage.env],
            copy_in=copy_in,
            copy_in_dir="." if task_stage.copy_in_cwd else "",
            copy_out=copy_out_files,
            copy_in_cached={file: file for file in cached},
            copy_out_cached=file_export,
            cpu_limit=task_stage.limit.cpu,
            clock_limit=task_stage.limit.time,
            memory_limit=task_stage.limit.mem,
            proc_limit=task_stage.limit.proc,
            stderr=result.Collector(
                name="stderr", pipe=True, max=task_stage.limit.stderr
            ),
            stdout=result.Collector(
                name="stdout", pipe=True, max=task_stage.limit.stdout
            ),
        ),
        cases=[],
    )
    for file in file_export:
        cached[file] = None
    return executor_with_config


def fix_keyword(
    keyword_config: task.ParserKeyword, keyword_parser: result.Parser
) -> None:
    if len(keyword_config.keyword) != len(keyword_config.weight):
        raise ValueError("Keywords and weights must have the same length")
    score_groups: Dict[int, List[str]] = {}
    for keyword, score in zip(keyword_config.keyword, keyword_config.weight):
        score_groups.setdefault(score, []).append(keyword)
    keyword_parser.with_ = result.KeywordMatchConfig(
        score=keyword_config.score,
        matches=[
            result.KeywordConfig(keywords=keywords, score=score)
            for score, keywords in score_groups.items()
        ],
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
    result_detail_parser.with_ = result.ResultDetailConfig(
        score=0,
        comment="",
        show_files=show_files,
        show_exit_status=result_detail_parser_config.exit_status,
        show_runtime=result_detail_parser_config.time,
        show_time=result_detail_parser_config.cpu_time,
        show_memory=result_detail_parser_config.mem,
        show_error=result_detail_parser_config.error,
        show_proc_peak=result_detail_parser_config.proc_peak,
        files_in_code_block=result_detail_parser_config.code_block,
        max_file_length=result_detail_parser_config.max_length,
    )


def fix_dummy(
    dummy_parser_config: task.ParserDummy, dummy_parser: result.Parser
) -> None:
    dummy_parser.with_ = result.DummyConfig(
        score=dummy_parser_config.score,
        comment=dummy_parser_config.comment,
        force_quit=dummy_parser_config.force_quit,
    )


def fix_result_status(
    result_status_parser_config: task.ParserResultStatus,
    result_status_parser: result.Parser,
) -> None:
    result_status_parser.with_ = result.ResultStatusConfig(
        score=result_status_parser_config.score,
        comment=result_status_parser_config.comment,
        force_quit_on_not_accepted=result_status_parser_config.force_quit,
    )


def fix_file(file_parser_config: task.ParserFile, file_parser: result.Parser) -> None:
    file_parser.with_ = result.FileConfig(name=file_parser_config.name)


def fix_diff(
    _: task.ParserDiff,
    diff_parser: result.Parser,
    task_stage: task.Stage,
    executor: result.Executor,
    task_root: Path,
    task_path: Path,
) -> None:
    base_dir = JOJ3_CONFIG_ROOT / task_path.parent
    # cases not specified in the toml config (auto-detected)
    unspecified_cases = get_unspecified_cases(task_root, task_path, task_stage.cases)
    # cases specified in toml config but not skipped
    specified_cases = [(case, task_stage.cases[case]) for case in task_stage.cases]
    stage_cases = []
    parser_cases = []
    for case_name, case in specified_cases:
        stdin, stdout = get_stdin_stdout(task_root, task_path, case_name, case)
        if stdout is None:
            logger.warning(
                f"In file {task_root / task_path}, "
                f"testcase {case_name} has no corresponding .out file, "
                "skipped"
            )
            continue
        cmd = result.OptionalCmd(
            stdin=stdin,
            args=shlex.split(case.command) if case.command else None,
            cpu_limit=case.limit.cpu,
            clock_limit=case.limit.time,
            memory_limit=case.limit.mem,
            proc_limit=task_stage.limit.proc,
        )
        if cmd.args == executor.with_.default.args:
            cmd.args = None
        if cmd.cpu_limit == executor.with_.default.cpu_limit:
            cmd.cpu_limit = None
        if cmd.clock_limit == executor.with_.default.clock_limit:
            cmd.clock_limit = None
        if cmd.memory_limit == executor.with_.default.memory_limit:
            cmd.memory_limit = None
        if cmd.proc_limit == executor.with_.default.proc_limit:
            cmd.proc_limit = None
        stage_cases.append(cmd)

        def get_diff_attribute(attribute_name: str) -> Any:
            if case.diff and attribute_name in case.diff.model_fields_set:
                return getattr(case.diff, attribute_name)
            return getattr(task_stage.diff, attribute_name)

        parser_case = result.DiffCasesConfig(
            outputs=[
                result.DiffOutputConfig(
                    score=get_diff_attribute("score"),
                    filename="stdout",
                    answer_path=stdout,
                    compare_space=not get_diff_attribute("ignore_spaces"),
                    always_hide=get_diff_attribute("hide"),
                    force_quit_on_diff=get_diff_attribute("force_quit"),
                    max_diff_length=get_diff_attribute("max_length"),
                    max_diff_lines=get_diff_attribute("max_lines"),
                    hide_common_prefix=get_diff_attribute("hide_common_prefix"),
                )
            ]
        )
        parser_cases.append(parser_case)
    for case_name in unspecified_cases:
        cmd = result.OptionalCmd(
            stdin=result.LocalFile(src=str(base_dir / f"{case_name}.in")),
        )
        stage_cases.append(cmd)
        parser_case = result.DiffCasesConfig(
            outputs=[
                result.DiffOutputConfig(
                    score=task_stage.diff.score,
                    filename="stdout",
                    answer_path=str(base_dir / f"{case_name}.out"),
                    compare_space=not task_stage.diff.ignore_spaces,
                    always_hide=task_stage.diff.hide,
                    force_quit_on_diff=task_stage.diff.force_quit,
                    max_diff_length=task_stage.diff.max_length,
                    max_diff_lines=task_stage.diff.max_lines,
                    hide_common_prefix=task_stage.diff.hide_common_prefix,
                )
            ]
        )
        parser_cases.append(parser_case)
    executor.with_.cases = stage_cases
    diff_parser.with_ = result.DiffConfig(name="diff", cases=parser_cases)


def get_unspecified_cases(
    task_root: Path, task_path: Path, cases: Dict[str, task.Case]
) -> List[str]:
    testcases = set()
    for testcases_path in (task_root / task_path).parent.glob("**/*.in"):
        if not testcases_path.with_suffix(".out").exists():
            logger.warning(
                f"In file {task_root / task_path}, "
                f"testcase {testcases_path} has no corresponding .out file, "
                "skipped"
            )
            continue
        testcases.add(
            str(
                PurePosixPath(
                    testcases_path.relative_to((task_root / task_path).parent)
                )
            ).removesuffix(".in")
        )
    return sorted(
        testcases.difference(
            [
                casei
                for casei in testcases
                if any(casei.endswith(casej) for casej in cases)
            ]
        )
    )


def get_stdin_stdout(
    task_root: Path, task_path: Path, case_name: str, case: task.Case
) -> Tuple[result.Stdin, Optional[str]]:
    base_dir = (task_root / task_path).parent
    stdin: result.Stdin = result.MemoryFile(content="")
    stdout = None
    for case_stdout_path in base_dir.glob("**/*.out"):
        if not case.out_:  # if not set, look for .out files with case name
            if case_stdout_path.name != f"{case_name}.out":
                continue
        else:  # if set, look for .out files with the same relative path
            if PurePosixPath(case.out_) != PurePosixPath(case_stdout_path).relative_to(
                base_dir
            ):
                continue
        stdout = str(JOJ3_CONFIG_ROOT / case_stdout_path.relative_to(task_root))
        case_stdin_path = case_stdout_path.with_suffix(".in")
        if case.in_:
            case_stdin_path = Path(base_dir / case.in_)
        if not case_stdin_path.exists():
            logger.warning(
                f"In file {task_root / task_path}, "
                f"testcase {case_stdout_path} has no .in file, "
                "use empty content as stdin"
            )
        else:
            stdin = result.LocalFile(
                src=str(
                    JOJ3_CONFIG_ROOT
                    / PurePosixPath(case_stdin_path.relative_to(task_root))
                )
            )
        break
    return stdin, stdout
