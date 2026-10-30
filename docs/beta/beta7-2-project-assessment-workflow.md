# Beta 7.2 — entrega, revisão e avaliação do projeto

## Estados e fronteiras

O serviço isolado mantém `AWAITING_REVIEW`, `NEEDS_REVISION` e `APPROVED`. `APPROVED` só é aceito pelo contrato quando a versão da rubrica está pedagogicamente aprovada e todas as evidências/regras obrigatórias são satisfeitas. A versão real da fonte é `PROPOSED`, então a API permite feedback e solicitação de revisão, mas responde `409` a uma tentativa de aprovação.

Cada nova entrega depois de `NEEDS_REVISION` ou feedback avaliado recebe nova identidade/tentativa e `previous_submission_id`; entregas anteriores permanecem consultáveis. Uma tentativa não pode ser criada enquanto a anterior está aguardando avaliação ou já está aprovada. A identidade do aluno vem da sessão autenticada, nunca do corpo enviado pelo cliente.

## Avaliação

`POST /api/beta7-2/assessment/batches/{batch_id}/project/submissions/{submission_id}/assess` exige sessão, permissão `submissions.grade`, grant sintético explícito da prévia, chave de idempotência e revisão esperada. A decisão e sua auditoria são gravadas na mesma transação que atualiza a revisão da submissão e incrementa a revisão do grant, que também funciona como fence contra revogação. O CAS evita confirmação dupla da mesma revisão. Retry idêntico recupera o mesmo recibo; mesma chave com payload divergente retorna conflito.

`GET .../project/rubric` é restrito a avaliador autorizado. `GET .../project/assessment-history/mine` é restrito ao histórico do aluno autenticado e omite critérios privados. A revisão com feedback não implica domínio nem conclusão.

O router fica montado somente pelo servidor test-only explicitamente composto após o gate de MongoDB descartável. Não é registrado no `server:app`, nas rotas de publicação nem no startup operacional.
