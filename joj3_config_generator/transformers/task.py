import re
import shlex
from functools import partial
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Dict, List, Set, Tuple

from joj3_config_generator.models import result, task
from joj3_config_generator.models.common import Memory, Time
from joj3_config_generator.models.const import (
    DEFAULT_CLOCK_LIMIT_MULTIPLIER,
    JOJ3_CONFIG_ROOT,
)
from joj3_config_generator.models.task import Parser as ParserEnum
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
) -> Dict[ParserEnum, Tuple[Callable[[Any, result.Parser], None], Any]]:
    return {
        ParserEnum.ELF: (fix_keyword, task_stage.elf),
        ParserEnum.CLANG_TIDY: (fix_keyword, task_stage.clangtidy),
        ParserEnum.KEYWORD: (fix_keyword, task_stage.keyword),
        ParserEnum.CPPCHECK: (fix_keyword, task_stage.cppcheck),
        ParserEnum.CPPLINT: (fix_keyword, task_stage.cpplint),
        ParserEnum.RESULT_DETAIL: (fix_result_detail, task_stage.result_detail),
        ParserEnum.DUMMY: (fix_dummy, task_stage.dummy),
        ParserEnum.RESULT_STATUS: (fix_dummy, task_stage.result_status),
        ParserEnum.FILE: (fix_file, task_stage.file),
        ParserEnum.DIFF: (
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
    file_import = task_stage.files.import_
    copy_in_files = (file for file in file_import if file not in cached)
    file_export = task_stage.files.export
    copy_out_files = ["stdout", "stderr"]
    executor_with_config = result.ExecutorWith(
        default=result.Cmd(
            args=shlex.split(task_stage.command),
            copy_in={
                file: result.LocalFile(src=str(JOJ3_CONFIG_ROOT / file))
                # all copyin files store in this tools folder
                # TODO: are there any corner cases?
                for file in copy_in_files
            },
            copy_out=copy_out_files,
            copy_in_cached={file: file for file in cached},
            copy_out_cached=file_export,
            cpu_limit=Time(task_stage.limit.cpu),
            clock_limit=DEFAULT_CLOCK_LIMIT_MULTIPLIER * Time(task_stage.limit.cpu),
            memory_limit=Memory(task_stage.limit.mem),
            proc_limit=task_stage.limit.proc,
            stderr=result.Collector(
                name="stderr", pipe=True, max=Memory(task_stage.limit.stderr)
            ),
            stdout=result.Collector(
                name="stdout", pipe=True, max=Memory(task_stage.limit.stdout)
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
        matches=[
            result.KeywordConfig(keywords=keywords, score=score)
            for score, keywords in score_groups.items()
        ]
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
    )


def fix_dummy(
    dummy_parser_config: task.ParserDummy, dummy_parser: result.Parser
) -> None:
    # we don't use dummy parser in real application
    dummy_parser.with_ = result.DummyConfig(
        score=dummy_parser_config.score,
        comment=dummy_parser_config.comment,
        force_quit_on_not_accepted=dummy_parser_config.force_quit,
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
    # all intended testcases that is detected
    testcases = get_testcases(task_root, task_path)
    # all testcases that is not specified in the toml config
    default_cases = sorted(
        testcases.difference(
            [
                casei
                for casei in testcases
                if any(casei.endswith(casej) for casej in task_stage.cases)
            ]
        )
    )
    # those in toml config that is not skiped
    valid_cases = [
        (casej, task_stage.cases[casei])
        for casei in task_stage.cases
        for casej in testcases
        if (casei not in task_stage.skip and casej.endswith(casei))
    ]
    stage_cases = []
    parser_cases = []
    for case, case_stage in valid_cases:
        cmd = result.OptionalCmd(
            stdin=result.LocalFile(
                src=str(base_dir / (case_stage.in_ or f"{case}.in"))
            ),
            args=shlex.split(case_stage.command) if case_stage.command else None,
            cpu_limit=case_stage.limit.cpu,
            clock_limit=DEFAULT_CLOCK_LIMIT_MULTIPLIER * case_stage.limit.cpu,
            memory_limit=case_stage.limit.mem,
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
        parser_case = result.DiffCasesConfig(
            outputs=[
                result.DiffOutputConfig(
                    score=case_stage.diff.output.score,
                    file_name="stdout",
                    answer_path=str(base_dir / (case_stage.out_ or f"{case}.out")),
                    force_quit_on_diff=case_stage.diff.output.force_quit,
                    always_hide=case_stage.diff.output.hide,
                    compare_space=not case_stage.diff.output.ignore_spaces,
                )
            ]
        )
        parser_cases.append(parser_case)
    for case in default_cases:
        cmd = result.OptionalCmd(
            stdin=result.LocalFile(src=str(base_dir / f"{case}.in")),
            cpu_limit=None,
            clock_limit=None,
            memory_limit=None,
            proc_limit=None,
        )
        stage_cases.append(cmd)
        parser_case = result.DiffCasesConfig(
            outputs=[
                result.DiffOutputConfig(
                    score=task_stage.diff.default_score,
                    file_name="stdout",
                    answer_path=str(base_dir / f"{case}.out"),
                )
            ]
        )
        parser_cases.append(parser_case)
    executor.with_.cases = stage_cases
    diff_parser.with_ = result.DiffConfig(name="diff", cases=parser_cases)


def get_testcases(
    task_root: Path, task_path: Path
) -> Set[str]:  # basedir here should be task_conf.root / task_conf.path
    testcases = set()
    for testcases_path in (task_root / task_path).parent.glob("**/*.in"):
        if not testcases_path.with_suffix(".out").exists():
            logger.warning(f"Testcase {testcases_path} has no corresponding .out file")
            continue
        testcases.add(
            str(
                PurePosixPath(
                    testcases_path.relative_to((task_root / task_path).parent)
                )
            ).removesuffix(".in")
        )
    return testcases
