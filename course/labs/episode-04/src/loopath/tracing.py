from pydantic import BaseModel, Field


class TraceStep(BaseModel):
    step: int
    action: dict
    result: dict


class Trace(BaseModel):
    task: str
    steps: list[TraceStep] = Field(default_factory=list)

    def add_step(self, step: int, action, result) -> None:
        self.steps.append(
            TraceStep(
                step=step,
                action=action.model_dump(),
                result=result.model_dump(),
            )
        )
