"""Deterministic, database-free evaluation for published multiple-choice activities."""

from typing import Any

EVALUATOR_VERSION = "multiple-choice.v1"


def evaluate_multiple_choice(definition: dict[str, Any], option_id: str) -> dict[str, Any]:
    """Evaluate one option against an immutable private definition.

    The result deliberately does not include the correct option identifier.
    Callers decide which configured feedback is safe to reveal for the current
    attempt policy.
    """
    options = definition.get("options")
    correct_option_id = definition.get("correct_option_id")
    if not isinstance(options, list) or not options or not isinstance(correct_option_id, str):
        raise ValueError("Definição de atividade inválida")
    option_ids = {
        option.get("id") for option in options
        if isinstance(option, dict) and isinstance(option.get("id"), str)
    }
    if correct_option_id not in option_ids:
        raise ValueError("Gabarito não pertence às alternativas")
    if not isinstance(option_id, str) or option_id not in option_ids:
        raise ValueError("Alternativa inexistente")

    is_correct = option_id == correct_option_id
    feedback = definition.get("feedback") or {}
    return {
        "is_correct": is_correct,
        "score": 100 if is_correct else 0,
        "feedback": feedback.get("correct" if is_correct else "incorrect", ""),
        "evaluator_version": definition.get("evaluator_version", EVALUATOR_VERSION),
    }
