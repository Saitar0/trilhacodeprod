import pytest

from activity_evaluator import evaluate_multiple_choice
from services.activity_publications import ActivityDefinitionError, normalize_quiz, public_activity


def _definition():
    return {
        "activity_id": "activity-1",
        "published_version_id": "version-1",
        "activity_revision": 1,
        "prompt": "Qual alternativa?",
        "options": [{"id": "alpha", "label": "A"}, {"id": "beta", "label": "B"}],
        "correct_option_id": "beta",
        "feedback": {"correct": "Isso.", "incorrect": "Revise o conceito."},
        "max_attempts": 2,
        "completion_policy": "responded",
        "evaluator_version": "multiple-choice.v1",
    }


def test_evaluator_accepts_answer_without_relying_on_option_order():
    result = evaluate_multiple_choice(_definition(), "beta")
    assert result == {
        "is_correct": True,
        "score": 100,
        "feedback": "Isso.",
        "evaluator_version": "multiple-choice.v1",
    }


def test_evaluator_returns_incorrect_result_without_revealing_answer_id():
    result = evaluate_multiple_choice(_definition(), "alpha")
    assert result["is_correct"] is False
    assert result["score"] == 0
    assert "correct_option_id" not in result


@pytest.mark.parametrize("option_id", ["missing", "", None])
def test_evaluator_rejects_unknown_or_invalid_options(option_id):
    with pytest.raises(ValueError, match="Alternativa inexistente"):
        evaluate_multiple_choice(_definition(), option_id)


def test_evaluator_rejects_definition_with_missing_gabarito():
    definition = _definition()
    definition["correct_option_id"] = "missing"
    with pytest.raises(ValueError, match="Gabarito"):
        evaluate_multiple_choice(definition, "alpha")


def test_new_activity_schema_is_strict_and_public_projection_hides_private_fields():
    block = {
        "_id": "block-1",
        "type": "quiz",
        "data": {
            "activity_schema_version": 1,
            "prompt": "Pergunta",
            "options": [{"id": "one", "label": "Primeira"}, {"id": "two", "label": "Segunda"}],
            "correct_option_id": "two",
            "feedback": {"correct": "Correto", "incorrect": "Tente novamente"},
            "completion_policy": "responded",
            "max_attempts": 2,
        },
    }
    definition = normalize_quiz(block, "published-1", 4)
    assert definition["correct_option_id"] == "two"
    assert definition["activity_revision"] == 4
    public = public_activity(definition)
    assert public["published_version_id"] == "published-1"
    assert "correct_option_id" not in public
    assert "feedback" not in public
    block["data"]["unexpected"] = "must reject"
    with pytest.raises(ActivityDefinitionError, match="campos não reconhecidos"):
        normalize_quiz(block, "published-2", 5)


def test_valid_legacy_quiz_gets_stable_option_ids_and_invalid_legacy_stays_static():
    valid = normalize_quiz({
        "_id": "legacy-block",
        "type": "quiz",
        "data": {"question": "Q", "options": ["A", "B"], "correct_index": 1, "explanation": "Explicação"},
    }, "version-1", 1)
    assert [option["id"] for option in valid["options"]] == ["option-1", "option-2"]
    assert valid["correct_option_id"] == "option-2"
    invalid = normalize_quiz({
        "_id": "bad-legacy",
        "type": "quiz",
        "data": {"question": "Q", "options": ["A"], "correct_index": 0},
    }, "version-1", 1)
    assert invalid is None
