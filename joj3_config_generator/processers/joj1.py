from typing import List

import humanfriendly
from pytimeparse.timeparse import timeparse

from joj3_config_generator.models import joj1, result, task


def get_joj1_run_stage(joj1_config: joj1.Config) -> task.Stage:
    default_cpu = timeparse("1s")
    default_mem = humanfriendly.parse_size("32m")
    cases_conf = []
    for i, case in enumerate(joj1_config.cases):
        cases_conf.append(
            task.Stage(
                score=case.score,
                command=case.execute_args if case.execute_args else None,
                limit=task.Limit(
                    cpu=timeparse(case.time) if case.time else default_cpu,
                    mem=(
                        humanfriendly.parse_size(case.memory)
                        if case.memory
                        else default_mem
                    ),
                ),
            )
        )
    for i, case in enumerate(joj1_config.cases):
        cases_conf[i].in_ = case.input
        cases_conf[i].out_ = case.output
    run_config = task.Stage(
        name="This is the converted joj1 run stage",
        group="joj",
        parsers=["diff", "result-status"],
        score=100,
        limit=task.Limit(
            cpu=(
                timeparse(joj1_config.cases[0].time)
                if joj1_config.cases[0].time is not None
                else default_cpu
            ),
            mem=(
                humanfriendly.parse_size(joj1_config.cases[0].memory)
                if joj1_config.cases[0].memory is not None
                else default_mem
            ),
        ),
        cases={f"case{i}": cases_conf[i] for i, case in enumerate(joj1_config.cases)},
    )
    return run_config
