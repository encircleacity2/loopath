from __future__ import annotations

import json
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter, ValidationError


class ReadFileAction(BaseModel):
    type: Literal["read_file"]
    path: str


class SearchAction(BaseModel):
    type: Literal["search"]
    query: str
    path: str | None = None


class RunCommandAction(BaseModel):
    type: Literal["run_command"]
    command: str


class EditFileAction(BaseModel):
    type: Literal["edit_file"]
    path: str
    content: str


class FinalAnswerAction(BaseModel):
    type: Literal["final_answer"]
    message: str


# A discriminated union: Pydantic uses the `type` field to pick the right model.
Action = Annotated[
    Union[
        ReadFileAction,
        SearchAction,
        RunCommandAction,
        EditFileAction,
        FinalAnswerAction,
    ],
    Field(discriminator="type"),
]

ACTION_ADAPTER = TypeAdapter(Action)


class ActionParseError(Exception):
    """Raised when model output is not a valid action.

    Two distinct failure classes are funneled here on purpose so the loop can
    map each to a different recovery prompt:
      1. the output is not valid JSON, and
      2. the JSON does not match the action schema.
    """


def parse_action(raw: str):
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ActionParseError(f"Model output is not valid JSON: {exc}") from exc

    try:
        return ACTION_ADAPTER.validate_python(data)
    except ValidationError as exc:
        raise ActionParseError(f"Model output does not match action schema: {exc}") from exc
