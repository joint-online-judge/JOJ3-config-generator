from joj3_config_generator.models import joj1, task
from joj3_config_generator.models.common import Memory, Time


def get_joj1_run_stage(joj1_config: joj1.Config) -> task.Stage:
    cases_conf = []
    for i, case in enumerate(joj1_config.cases):
        cases_conf.append(
            task.Stage(
                score=case.score,
                command=case.execute_args if case.execute_args else "",
                limit=task.Limit(cpu=Time(case.time), mem=Memory(case.memory)),
            )
        )
    for i, case in enumerate(joj1_config.cases):
        cases_conf[i].in_ = case.input
        cases_conf[i].out_ = case.output
    run_config = task.Stage(
        name="This is the converted joj1 run stage",
        parsers=["diff", "result-status"],
        score=100,
        limit=task.Limit(
            cpu=Time(joj1_config.cases[0].time),
            mem=Memory(joj1_config.cases[0].memory),
        ),
        cases={f"case{i}": cases_conf[i] for i, _ in enumerate(cases_conf)},
    )  # TODO: no strong pattern match here, use dict instead
    return run_config


# TODO: get formatted joj1 config, match the criterion in the doc
