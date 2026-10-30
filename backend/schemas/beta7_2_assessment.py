"""HTTP inputs for the isolated versioned project assessment surface."""

from pydantic import BaseModel, ConfigDict, Field

from curriculum_contract.beta7_2_assessment import AssessmentOutcome, CriterionEvidence


class ProjectAssessmentIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    project_version: str = Field(min_length=1, max_length=128)
    rubric_id: str = Field(min_length=1, max_length=128)
    rubric_version: str = Field(min_length=1, max_length=128)
    expected_revision: int = Field(ge=0)
    outcome: AssessmentOutcome
    feedback: str = Field(min_length=1, max_length=20_000)
    criteria: tuple[CriterionEvidence, ...] = ()
