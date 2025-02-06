from typing import List

from pydantic import BaseModel, Field


class Files(BaseModel):
    required: List[str]
    immutable: List[str]


class Group(BaseModel):
    name: List[str]
    max_count: List[int]
    time_period_hour: List[int]


class Config(BaseModel):
    max_size: float = Field(..., ge=0)
    files: Files
    sandbox_token: str
    max_total_score: int = Field(100)
    groups: Group
