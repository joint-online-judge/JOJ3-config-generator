from joj3_config_generator.models.result import Stage as ResultStage
from joj3_config_generator.models.task import Stage as TaskStage


def fix_keyword(task_stage: TaskStage, conf_stage: ResultStage) -> ResultStage:
    keyword_parser = ["clangtidy", "keyword", "cppcheck"]  # TODO: may add cpplint
    for parser in task_stage.parsers:
        if parser in keyword_parser:
            keyword_parser_ = next(p for p in conf_stage.parsers if p.name == parser)
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


def fix_comment(task_stage: TaskStage, conf_stage: ResultStage) -> ResultStage:
    comment_parser = [
        "dummy",
        "result-status",
        "cpplint",
    ]  # FIXME: determine where cpplint should be
    for parser in task_stage.parsers:
        if parser in comment_parser:
            comment_parser_ = next(p for p in conf_stage.parsers if p.name == parser)
            if getattr(task_stage, parser.replace("-", "_"), None) is not None:
                comment_parser_.with_.update(
                    getattr(task_stage, parser.replace("-", "_"))
                )
        else:
            continue
    return conf_stage
