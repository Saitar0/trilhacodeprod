"""HTTP assertions against the attested local API and disposable MongoDB."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

API = "http://127.0.0.1:18000"
ORIGIN = "http://127.0.0.1:3000"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def login(client: httpx.Client, email: str, password: str) -> dict[str, Any]:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    detail = None
    try:
        body = response.json()
        detail = body.get("detail") if isinstance(body, dict) else None
    except ValueError:
        pass
    if isinstance(detail, list):
        safe_items = [
            {key: item.get(key) for key in ("loc", "type", "msg") if key in item}
            for item in detail if isinstance(item, dict)
        ]
        detail = "validation=" + json.dumps(safe_items, ensure_ascii=True)[:300]
    elif detail not in {
        "Not Found", "Email ou senha inválidos", "Confirme seu e-mail para acessar a plataforma",
    }:
        detail = "resposta sem detalhe reconhecido"
    require(response.status_code == 200, f"Login sintético falhou ({response.status_code}; {detail})")
    return response.json()


def main() -> int:
    batch_id = os.environ["BETA7_1_E2E_BATCH_ID"]
    private_track_id = os.environ["BETA7_1_E2E_PRIVATE_TRACK_ID"]
    student = httpx.Client(base_url=API, trust_env=False)
    login(student, "beta7-1-student@example.com", os.environ["BETA7_1_STUDENT_PASSWORD"])
    tree = student.get(f"/api/beta7-1/preview/batches/{batch_id}")
    require(tree.status_code == 200, "Aluno sintético autorizado não leu a árvore da prévia")
    phase = tree.json()
    require(len(phase["modules"]) == 3, "Árvore HTTP não contém três módulos")
    require(sum(len(module["units"]) for module in phase["modules"]) == 10, "Árvore HTTP não contém dez unidades")

    private = student.get(f"/api/tracks/{private_track_id}/tree")
    require(private.status_code == 404, "Leitor operacional deixou escapar a trilha privada em rascunho")
    first = student.get(f"/api/beta7-1/preview/batches/{batch_id}/units/1.1")
    require(first.status_code == 200, "Unidade 1.1 não foi servida pela API de prévia")
    unit = first.json()
    require((len(unit["topics"]), sum(len(topic["segments"]) for topic in unit["topics"])) == (5, 8),
            "Estrutura teórica 1.1 divergiu da fonte")
    require((len(unit["quizzes"]), len(unit["exercises"])) == (5, 3), "Atividades da 1.1 divergiram da fonte")
    serialized = json.dumps(unit, ensure_ascii=False)
    for hidden in ("correct_option_id", "explanation", "private_materials", "restricted_content", "answer_key"):
        require(hidden not in serialized, f"Campo restrito exposto na resposta pública: {hidden}")

    question = unit["quizzes"][0]
    attempt = student.post(
        f"/api/beta7-1/preview/batches/{batch_id}/units/1.1/quizzes/{question['id']}/attempts",
        json={"source_sha256": question["version"], "selected_option_id": question["options"][0]["id"]},
        headers={"Origin": ORIGIN, "Idempotency-Key": "beta71-http-quiz-0001"},
    )
    require(attempt.status_code == 200, "Tentativa de quiz não foi registrada por HTTP")
    receipt = attempt.json()
    require(receipt["state"] == "ANSWERED" and "is_correct" not in receipt,
            "Recibo de quiz revelou acerto antes de política pedagógica")

    exercise = unit["exercises"][0]
    submitted = student.post(
        f"/api/beta7-1/preview/batches/{batch_id}/units/1.1/exercises/{exercise['id']}/submissions",
        json={"source_sha256": exercise["version"], "unit_source_sha256": unit["version"],
              "answer_text": "Entrega textual sintética da Beta 7.1."},
        headers={"Origin": ORIGIN, "Idempotency-Key": "beta71-http-exercise-0001"},
    )
    require(submitted.status_code == 200 and submitted.json()["state"] == "AWAITING_REVIEW",
            "Exercício não permaneceu aguardando correção")

    project = student.get(f"/api/beta7-1/preview/batches/{batch_id}/project")
    require(project.status_code == 200, "Brief do projeto não foi servido ao aluno autorizado")
    public_artifacts = project.json()["artifacts"]
    public_json = json.dumps(project.json(), ensure_ascii=False).casefold()
    require(len(public_artifacts) == 1 and public_artifacts[0]["kind"] == "project_brief"
            and "rubrica" not in public_json and "checklist" not in public_json,
            "Materiais do projeto sem política aprovada foram expostos ao aluno")
    denied = student.get(f"/api/beta7-1/preview/batches/{batch_id}/project/restricted")
    require(denied.status_code == 403, "Aluno recebeu acesso ao material restrito do projeto")
    delivery = student.post(
        f"/api/beta7-1/preview/batches/{batch_id}/project/submissions",
        json={"source_sha256": project.json()["version"], "delivery_text": "Entrega sintética do projeto 3.5."},
        headers={"Origin": ORIGIN, "Idempotency-Key": "beta71-http-project-0001"},
    )
    require(delivery.status_code == 200 and delivery.json()["state"] == "AWAITING_REVIEW",
            "Entrega do projeto não permaneceu aguardando avaliação")
    project_submission_id = delivery.json()["id"]
    student.close()

    unscoped = httpx.Client(base_url=API, trust_env=False)
    login(unscoped, "beta7-1-unscoped@example.com", os.environ["BETA7_1_UNSCOPED_PASSWORD"])
    denied_tree = unscoped.get(f"/api/beta7-1/preview/batches/{batch_id}")
    require(denied_tree.status_code == 404, "Usuário sintético sem escopo acessou a prévia")
    unscoped.close()

    reviewer = httpx.Client(base_url=API, trust_env=False)
    login(reviewer, "beta7-1-reviewer@example.com", os.environ["BETA7_1_REVIEWER_PASSWORD"])
    queue = reviewer.get(f"/api/beta7-1/preview/batches/{batch_id}/project/review-queue")
    require(queue.status_code == 200 and any(row["id"] == project_submission_id for row in queue.json()),
            "Avaliador autorizado não recebeu a entrega no escopo")
    detail = reviewer.get(
        f"/api/beta7-1/preview/batches/{batch_id}/project/submissions/{project_submission_id}"
    )
    require(detail.status_code == 200 and any(
        item["classification"] == "INSTRUCTOR_RESTRICTED" for item in detail.json()["restricted_materials"]
    ), "Avaliador autorizado não recebeu os materiais restritos")
    graded = reviewer.post(
        f"/api/beta7-1/preview/batches/{batch_id}/project/submissions/{project_submission_id}/review",
        json={"expected_revision": 0, "outcome": "needs_revision", "feedback": "Revisão sintética para validar o fluxo."},
        headers={"Origin": ORIGIN, "Idempotency-Key": "beta71-http-review-0001"},
    )
    try:
        graded_body = graded.json()
    except ValueError:
        graded_body = {}
    safe_state = graded_body.get("state") if isinstance(graded_body, dict) else None
    safe_detail = graded_body.get("detail") if isinstance(graded_body, dict) else None
    if safe_state not in {"NEEDS_REVISION", "AWAITING_REVIEW", "REVIEWED_FEEDBACK_ONLY"}:
        safe_state = "unknown"
    if safe_detail not in {
        "Entrega não encontrada", "Permissão insuficiente", "A entrega foi alterada por outra avaliação",
        "Conflito de avaliação ou autorização; recarregue a entrega", "Origem da requisição não autorizada",
    }:
        safe_detail = "none"
    require(graded.status_code == 200 and safe_state == "NEEDS_REVISION",
            f"Correção manual autorizada não foi persistida (HTTP {graded.status_code}; "
            f"state={safe_state}; detail={safe_detail}; content_type={graded.headers.get('content-type', 'none')})")
    reviewer.close()

    student_again = httpx.Client(base_url=API, trust_env=False)
    login(student_again, "beta7-1-student@example.com", os.environ["BETA7_1_STUDENT_PASSWORD"])
    own = student_again.get(f"/api/beta7-1/preview/batches/{batch_id}/project/submissions/mine")
    require(own.status_code == 200 and any(
        item["id"] == project_submission_id and item["feedback"] == "Revisão sintética para validar o fluxo."
        for item in own.json()
    ), "Feedback não sobreviveu à nova sessão do aluno")
    progress = student_again.get(f"/api/beta7-1/preview/batches/{batch_id}/progress")
    require(progress.status_code == 200 and progress.json()["phase"]["completion"] ==
            "BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA", "Progresso declarou conclusão sem critérios definidos")
    student_again.close()

    print(json.dumps({
        "status": "HTTP_VERIFIED",
        "modules": len(phase["modules"]),
        "units": sum(len(module["units"]) for module in phase["modules"]),
        "unit_1_1_topics": len(unit["topics"]),
        "unit_1_1_segments": sum(len(topic["segments"]) for topic in unit["topics"]),
        "unit_1_1_questions": len(unit["quizzes"]),
        "unit_1_1_exercises": len(unit["exercises"]),
        "operational_private_reader": private.status_code,
        "project_review": graded.json()["state"],
        "student_feedback_after_new_session": True,
    }, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
