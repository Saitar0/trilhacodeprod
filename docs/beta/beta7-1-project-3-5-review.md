# Beta 7.1 — projeto 3.5: visibilidade, entrega e correção

## Materiais e política

O inventário tipado confirma 11 materiais: um brief, quatro marcos, uma rubrica e cinco checklists. O aluno recebe somente o brief, e apenas dentro do grant da prévia. A projeção pública é allowlist por tipo; materiais sem regra comprovada de liberação não têm nem título/ID expostos. A rota restrita exige permissão de revisão e escopo de lote. A rubrica é classificada como material reservado ao avaliador.

Os quatro marcos não têm uma regra de progressão comprovada e os cinco checklists ainda não possuem classificação editorial aprovada para exibição. Permanecem ocultos. Nenhuma regra de desbloqueio foi inventada.

## Fluxo validado

Em MongoDB descartável, aluno sintético autenticado enviou uma entrega textual versionada; estado inicial `AWAITING_REVIEW`. O avaliador sintético com grant de revisão abriu a entrega e os materiais restritos, registrou feedback e solicitou revisão. A entrega passou a `NEEDS_REVISION`; o aluno consultou o feedback em nova sessão. O histórico/auditoria permaneceu associado à identidade do avaliador e à entrega. A chave de idempotência e a revisão do documento foram validadas.

Não há upload de executáveis, execução de código, integração de avaliação automática ou exposição de rubrica ao aluno. Os testes HTTP e Playwright percorreram o fluxo. A decisão de aprovação não foi habilitada: os critérios da rubrica não sustentam uma regra de aprovação objetiva aprovada pelo responsável pedagógico.

## Veredito

**PROJETO 3.5 PARCIALMENTE VALIDADO — AVALIAÇÃO OU CRITÉRIOS PENDENTES**. Entrega e feedback humano funcionam na prévia isolada; a aprovação pedagógica e a política de progressão dos marcos continuam bloqueadas.
