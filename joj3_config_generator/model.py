from datetime import datetime
from typing import List, Optional

import rtoml
from pydantic import BaseModel, Field


class RepoFiles(BaseModel):
    whitelist_patterns: List[str]
    whitelist_file: Optional[str]
    required: List[str]
    immutable: List[str]


class Repo(BaseModel):
    teaching_team: List[str]
    max_size: float = Field(..., ge=0)
    release_tags: List[str]
    files: RepoFiles


class ParserResultDetail(BaseModel):
    time: bool = True  # Display run time
    mem: bool = True  # Display memory usage
    stderr: bool = False  # Display stderr messages


class Files(BaseModel):
    import_: List[str] = Field(alias="import")
    export: List[str]


class Stage(BaseModel):
    name: str  # Stage name
    command: str  # Command to run
    files: Files  # Files to import and export
    score: int  # Score for the task
    parsers: List[str]  # List of parsers
    result_detail: ParserResultDetail = (
        ParserResultDetail()
    )  #  for result-detail parser


class Release(BaseModel):
    deadline: Optional[datetime]  # RFC 3339 formatted date-time with offset


class Task(BaseModel):
    task: str  # Task name (e.g., hw3 ex5)
    release: Release  # Release configuration
    stages: List[Stage]  # List of stage configurations


if __name__ == "__main__":
    repo_toml = """
teaching_team = [ "prof_john", "ta_alice", "ta_bob" ]
max_size = 50.5
release_tags = [ "v1.0", "v2.0", "final" ]

[files]
whitelist_patterns = [ "*.py", "*.txt", "*.md" ]
whitelist_file = ".whitelist"
required = [ "main.py", "README.md" ]
immutable = [ "config.yaml", "setup.py" ]
"""
    task_toml = """
task = "hw3 ex5"

[release]
deadline = "2024-10-18T23:59:00+08:00"

[[stages]]
name = "judge_base"
command = "./matlab-joj ./h3/ex5.m"
score = 100
parsers = [ "diff", "result-detail" ]

files.import = [ "tools/matlab-joj", "tools/matlab_formatter.py" ]
files.export = [ "output/ex5_results.txt", "output/ex5_logs.txt" ]

result_detail.time = false
result_detail.mem = false
result_detail.stderr = true

[[stages]]
name = "judge_base2"
command = "./matlab-joj ./h3/ex5.m"
score = 80
parsers = [ "diff", "result-detail" ]

files.import = [ "tools/matlab-joj", "tools/matlab_formatter.py" ]
files.export = [ "output/ex5_results2.txt", "output/ex5_logs2.txt" ]

result_detail.time = true
result_detail.mem = true
result_detail.stderr = false
"""
    repo_obj = rtoml.loads(repo_toml)
    task_obj = rtoml.loads(task_toml)
    print(Repo(**repo_obj))
    print(Task(**task_obj))
