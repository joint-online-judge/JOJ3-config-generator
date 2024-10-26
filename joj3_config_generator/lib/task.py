import rtoml

from joj3_config_generator.models.result import CmdFile, OptionalCmd
from joj3_config_generator.models.result import Stage as ResultStage
from joj3_config_generator.models.task import Stage as TaskStage


def fix_keyword(task_stage: TaskStage, conf_stage: ResultStage) -> ResultStage:
    keyword_parser = ["clangtidy", "keyword", "cppcheck"]  # TODO: may add cpplint
    if task_stage.parsers is not None:
        for parser in task_stage.parsers:
            if parser in keyword_parser:
                keyword_parser_ = next(
                    p for p in conf_stage.parsers if p.name == parser
                )
                keyword_weight = []
                if getattr(task_stage, parser, None) is not None:
                    for _, keyword in enumerate(getattr(task_stage, parser).keyword):
                        keyword_weight.append({"keyword": [keyword], "score": 0})
                    for idx, weight in enumerate(getattr(task_stage, parser).weight):
                        keyword_weight[idx]["score"] = weight

                keyword_parser_.with_.update({"match": keyword_weight})
            else:
                continue
    return conf_stage


def fix_result_detail(task_stage: TaskStage, conf_stage: ResultStage) -> ResultStage:
    if (task_stage.parsers is not None) and ("result-detail" in task_stage.parsers):
        result_detail_parser = next(
            p for p in conf_stage.parsers if p.name == "result-detail"
        )
        if task_stage.result_detail is not None:
            show_files = []
            if (
                task_stage.result_detail.stdout
                and task_stage.result_detail.stdout is not None
            ):
                show_files.append("stdout")
            if (
                task_stage.result_detail.stderr
                and task_stage.result_detail.stderr is not None
            ):
                show_files.append("stderr")
            result_detail_parser.with_.update(
                {
                    "score": 0,
                    "comment": "",
                    "showFiles": show_files,
                    "showExitStatus": task_stage.result_detail.exitstatus,
                    "showRuntime": task_stage.result_detail.time,
                    "showMemory": task_stage.result_detail.mem,
                }
            )

    return conf_stage


def fix_comment(task_stage: TaskStage, conf_stage: ResultStage) -> ResultStage:
    comment_parser = [
        "dummy",
        "result-status",
        "cpplint",
    ]  # FIXME: determine where cpplint should be
    if task_stage.parsers is not None:
        for parser in task_stage.parsers:
            if parser in comment_parser:
                comment_parser_ = next(
                    p for p in conf_stage.parsers if p.name == parser
                )
                if getattr(task_stage, parser.replace("-", "_"), None) is not None:
                    comment_parser_.with_.update(
                        getattr(task_stage, parser.replace("-", "_"))
                    )
            else:
                continue
    return conf_stage


def fix_diff(task_stage: TaskStage, conf_stage: ResultStage) -> ResultStage:
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

            # Ensure case_stage.limit is defined before accessing .cpu and .mem
            cpu_limit = (
                case_stage.limit.cpu * 1_000_000_000
                if case_stage.limit and case_stage.limit.cpu is not None
                else 0
            )
            clock_limit = (
                2 * case_stage.limit.cpu * 1_000_000_000
                if case_stage.limit and case_stage.limit.cpu is not None
                else 0
            )
            memory_limit = (
                case_stage.limit.mem * 1_024 * 1_024
                if case_stage.limit and case_stage.limit.mem is not None
                else 0
            )

            stage_cases.append(
                OptionalCmd(
                    stdin=CmdFile(
                        src=f"/home/tt/.config/joj/{conf_stage.name}/{case}.in"
                    ),
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
                            {
                                "score": diff_output.score,
                                "fileName": "stdout",
                                "answerPath": f"/home/tt/.config/joj/{conf_stage.name}/{case}.out",
                                "forceQuitOnDiff": diff_output.forcequit,
                                "alwaysHide": diff_output.hide,
                                "compareSpace": not diff_output.ignorespaces,
                            }
                        ]
                    }
                )

        if diff_parser and task_stage.diff is not None:
            diff_parser.with_.update({"name": "diff", "cases": parser_cases})
            conf_stage.executor.with_.cases = stage_cases

    return conf_stage
