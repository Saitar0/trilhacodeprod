"""Validation and immutable read-model construction for published quizzes."""

import json
from hashlib import sha256
from typing import Any

from activity_evaluator import EVALUATOR_VERSION

MAX_ACTIVITY_BYTES = 96 * 1024
MAX_PROMPT_LENGTH = 20_000
MAX_OPTION_LENGTH = 2_000
MAX_FEEDBACK_LENGTH = 8_000
MIN_OPTIONS = 2
MAX_OPTIONS = 8
MAX_ATTEMPTS = 10


class ActivityDefinitionError(ValueError):
    """A versioned activity definition is marked new but violates its schema."""


def _text(value: Any, field: str, maximum: int, *, required: bool = False) -> str:
    if not isinstance(value, str) or (required and not value.strip()) or len(value) > maximum:
        raise ActivityDefinitionError(f"Campo {field} inválido")
    return value


def _options(options: Any, *, legacy: bool) -> list[dict[str, str]]:
    if not isinstance(options, list) or not MIN_OPTIONS <= len(options) <= MAX_OPTIONS:
        raise ActivityDefinitionError("A atividade deve ter de 2 a 8 alternativas")
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, option in enumerate(options):
        if legacy:
            option_id = f"option-{index + 1}"
            label = _text(option, "options", MAX_OPTION_LENGTH, required=True)
        else:
            if not isinstance(option, dict) or set(option) != {"id", "label"}:
                raise ActivityDefinitionError("Cada alternativa deve conter somente id e label")
            option_id = option.get("id")
            if not isinstance(option_id, str) or not option_id.isascii() or not 1 <= len(option_id) <= 64:
                raise ActivityDefinitionError("Identificador de alternativa inválido")
            label = _text(option.get("label"), "options.label", MAX_OPTION_LENGTH, required=True)
        if option_id in seen:
            raise ActivityDefinitionError("Identificadores de alternativas devem ser únicos")
        seen.add(option_id)
        normalized.append({"id": option_id, "label": label})
    return normalized


def normalize_quiz(block: dict, published_version_id: str, revision: int) -> dict | None:
    """Build a private, version-pinned definition; invalid legacy quizzes stay static.

    A block with ``activity_schema_version`` opts into the strict new contract:
    invalid data blocks publication. Unmarked historical ``quiz`` blocks are
    adapted only when their legacy fields are valid; otherwise they return None
    and remain ordinary non-evaluated content.
    """
    if block.get("type") != "quiz":
        return None
    data = block.get("data")
    if not isinstance(data, dict):
        return None

    versioned = "activity_schema_version" in data
    try:
        if versioned:
            allowed = {
                "activity_schema_version", "prompt", "options", "correct_option_id", "feedback",
                "completion_policy", "max_attempts",
            }
            if set(data) - allowed:
                raise ActivityDefinitionError("A definição versionada contém campos não reconhecidos")
            if type(data.get("activity_schema_version")) is not int or data["activity_schema_version"] != 1:
                raise ActivityDefinitionError("Versão de esquema de atividade não suportada")
            prompt = _text(data.get("prompt"), "prompt", MAX_PROMPT_LENGTH, required=True)
            options = _options(data.get("options"), legacy=False)
            correct_option_id = data.get("correct_option_id")
            if not isinstance(correct_option_id, str) or correct_option_id not in {item["id"] for item in options}:
                raise ActivityDefinitionError("Gabarito deve identificar uma das alternativas")
            completion_policy = data.get("completion_policy", "responded")
            if completion_policy != "responded":
                raise ActivityDefinitionError("completion_policy não suportada")
            max_attempts = data.get("max_attempts", 3)
            if type(max_attempts) is not int or not 1 <= max_attempts <= MAX_ATTEMPTS:
                raise ActivityDefinitionError("max_attempts deve estar entre 1 e 10")
            feedback = data.get("feedback", {})
            if not isinstance(feedback, dict) or set(feedback) - {"correct", "incorrect"}:
                raise ActivityDefinitionError("Feedback deve conter somente correct e incorrect")
            feedback = {
                key: _text(feedback.get(key, ""), f"feedback.{key}", MAX_FEEDBACK_LENGTH)
                for key in ("correct", "incorrect")
            }
        else:
            prompt = _text(data.get("question"), "question", MAX_PROMPT_LENGTH, required=True)
            options = _options(data.get("options"), legacy=True)
            correct_index = data.get("correct_index")
            if isinstance(correct_index, float) and correct_index.is_integer():
                correct_index = int(correct_index)
            if type(correct_index) is not int or not 0 <= correct_index < len(options):
                raise ActivityDefinitionError("correct_index inválido")
            correct_option_id = options[correct_index]["id"]
            explanation = _text(data.get("explanation", ""), "explanation", MAX_FEEDBACK_LENGTH)
            feedback = {"correct": explanation, "incorrect": explanation}
            completion_policy = "responded"
            max_attempts = 3

        block_id = block.get("_id", block.get("id"))
        if block_id is None:
            raise ActivityDefinitionError("Identificador de atividade ausente")
        definition = {
            "activity_id": str(block_id),
            "activity_schema_version": 1,
            "published_version_id": published_version_id,
            "activity_revision": revision,
            "prompt": prompt,
            "options": options,
            "correct_option_id": correct_option_id,
            "feedback": feedback,
            "completion_policy": completion_policy,
            "max_attempts": max_attempts,
            "evaluator_version": EVALUATOR_VERSION,
        }
        encoded = json.dumps(definition, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if len(encoded.encode("utf-8")) > MAX_ACTIVITY_BYTES:
            raise ActivityDefinitionError("Definição de atividade excede o limite permitido")
        definition["definition_sha256"] = sha256(encoded.encode("utf-8")).hexdigest()
        return definition
    except (ActivityDefinitionError, KeyError, TypeError, ValueError) as exc:
        if versioned:
            if isinstance(exc, ActivityDefinitionError):
                raise
            raise ActivityDefinitionError("Definição versionada inválida") from exc
        return None


def is_valid_legacy_quiz(block: dict) -> bool:
    """Whether an unversioned legacy quiz is valid enough for automatic grading."""
    if block.get("type") != "quiz" or "activity_schema_version" in (block.get("data") or {}):
        return False
    try:
        return normalize_quiz(block, "legacy-check", 0) is not None
    except ActivityDefinitionError:
        return False


def is_assessment_candidate(block: dict) -> bool:
    """Recognize valid legacy quizzes and all explicitly versioned quizzes."""
    data = block.get("data")
    return block.get("type") == "quiz" and isinstance(data, dict) and (
        "activity_schema_version" in data or is_valid_legacy_quiz(block)
    )


def public_activity(definition: dict) -> dict:
    """Return only the learner-facing immutable view, never assessment secrets."""
    digest = definition.get("definition_sha256")
    if digest is not None:
        canonical = {key: value for key, value in definition.items() if key != "definition_sha256"}
        encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if sha256(encoded.encode("utf-8")).hexdigest() != digest:
            raise ValueError("Definição publicada corrompida")
    return {
        key: definition[key]
        for key in (
            "activity_id", "activity_schema_version", "published_version_id", "activity_revision",
            "prompt", "options", "completion_policy", "max_attempts", "evaluator_version",
        )
    }
