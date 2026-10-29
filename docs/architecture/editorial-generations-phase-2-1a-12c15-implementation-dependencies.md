# Fase 2.1A.12C.15 — Dependências de implementação editorial

**Plano futuro, não autorização.** A ordem reflete dependências entre autoridades e writers identificadas em C13/C14. Nenhuma onda de mutação pode começar enquanto o mesmo estado permanecer gravável por caminho não coberto.

## Sequência por dependência

| Etapa | Escopo e pré-requisitos | Saída/critério de fechamento | Bloqueios e rollback |
|---|---|---|---|
| 0. Ratificar governança | P1–P8 estão ratificadas como política; nomear owner/IAM/security/product/privacy, RACI, admin global, delegação, recuperação e emergência. | Decisões assinadas com responsável e lifecycle; nenhuma auto-concessão/escalonamento. | Se faltarem decisores, nenhum grant operacional. Rollback documental: preservar versão/decisão anterior sem ativar nada. |
| 1. Fonte/forma do grant | Aprovar autoridade primária, relação a `users`/`auth_sessions`, unicidade, epoch, índices, referências e auditoria; validar no baseline autorizado ADR-008. | Schema e transação demonstrados com papéis DB/topologia compatíveis, sem fonte contraditória. | Schema/topologia/grants reais desconhecidos bloqueiam; nenhuma migration nesta C15. |
| 2. Ordenação IAM/policy | Definir como grant, papel, usuário, sessão, scope global e matriz Python mudam frente ao commit. Recomendada política híbrida epoch + drain. | Corridas concorrentes com todas as fontes requeridas; unknown commit reconciliável; versão antiga não confirma. | Falta de participação ou drain provado bloqueia. Rollback mantém epoch/revogações; retomar apenas writers compatíveis. |
| 3. Capability e auditoria | Emissor server-side; capability ligada a ator/sessão/policy/track/op/grant epoch/revision/fence; auditoria governança separada da editorial, ambas com falha definida. | Testes negativos de forja/ator/trilha e falha de audit transacional; ACL/retention aprovada. | Capability antiga não sobrevive revogação; sem ACL/key lifecycle não persistir receipts operacionais. |
| 4. HTTP e clientes | Aprovar API versionada/compatibilidade, `If-Match`, `Idempotency-Key`, null/absent, conflitos, replay e resposta mínima. | Clientes antigos identificados; sem escrita silenciosa sem precondição; documentação de erro e replay validada. | Legacy client não deve contornar. Pausar nova entrada em rollback, não reabrir writer antigo. |
| 5. Reconciliar e conter writers | Baseline de routes/jobs/CLI/seed/import/restore/operadores; identificar todos writers por coleção/scope; escolher adaptação ou bloqueio verificável. | Cada writer no scope adaptado ou incapaz tecnicamente de escrever; comprovado no alvo. | Qualquer caminho desconhecido ou bypass bloqueia. Observabilidade não substitui contenção. |
| 6. Writers simples de conteúdo/estrutura | Somente após etapa 5: família delimitada de W-01/W-05/W-07/W-08 conforme interseção comprovada, CAS/fence, audit, idempotência e compatibilidade. | Unit, persistente, conflito, falha, auth/revocation, regressões e concorrência passam no alvo compatível. | Não escolher W-07 isolado enquanto outros writers tocam `content_blocks`; correção é nova revisão, nunca apagar commit/audit. |
| 7. Catálogo, import e duplicação | W-03/W-09/W-10; autorização origem/destino e global; staging e ativação recuperáveis; dependem de etapas 1–6. | Failure matrix e retries mostram estado completo antigo ou operação concluída; nenhum partial visible. | Se coleção transversal ou efeito externo não coordena, manter bloqueado/restringido. |
| 8. Snapshot, restore, publish e readers | W-04/W-11/W-12/W-15; revision de origem, generation imutável, head atômico, readers pinados, activity/quiz. | Testes persistentes de concorrência/falhas, reader generation e tentativas; candidate nunca público parcialmente. | Maior blast radius; retirada emergencial explicitamente governada; nunca usar snapshot unit test como prova total. |
| 9. Exclusões, seeds e migrações | W-02/W-06/W-13/W-14; política de retenção/aluno, target allowlist, identidade e recuperação. | Cada etapa idempotente/recuperável, sem perda de tentativas e sem execução no alvo errado. | Operação irreversível sem compensação aprovada bloqueia; migration/seed apenas por autorização específica. |
| 10. Cutover/expansão | Depois de todas as dependências relevantes: rollout, monitoring, pause, reconciliation, rollback e suporte. | Baseline, gates aplicáveis, evidência operacional e aprovação específica de implantação. | ADR-008 bloqueado impede; nenhuma feature flag isolada vale como rollback ou bypass containment. |

Dependência abreviada: `0 → 1 → 2 → 3 → 4 → 5 → (6,7,8,9 conforme grafo de coleções) → 10`. Etapa 6 não pode ser ativada antes da contenção de todos writers concorrentes do seu escopo; etapa 8 depende de 6/7 e de readers; etapa 9 exige política de dados de aluno e recuperação.

## Política de rollback comum

1. Pausar entrada de mutações no scope e aguardar operações em voo ou marcá-las para reconciliação estável.
2. Bloquear efetivamente writers antigos em HTTP, workers, CLI, seed, import, restore e credenciais de execução; flag de rota isolada é insuficiente.
3. Para resultado de commit incerto, consultar recibo por ID interno estável; não repetir a mutação às cegas.
4. Preservar revisão, auditoria, histórico, grants revogados e receipts confirmados. Não decrementar epoch/reabrir permissão revogada.
5. Corrigir conteúdo por nova revisão auditada; não apagar confirmação anterior para imitar rollback.
6. Reabrir apenas versão de writer comprovadamente compatível e após regressões necessárias.

Pontos potencialmente irreversíveis: conteúdo publicado/visível, exclusão de track/node, alteração de tentativas/progresso, exposição de dados, gravação de auditoria e decisão de grant. Retirada pública e recuperação precisam de política de produto antes das etapas correspondentes.

## Critérios comuns de saída futura

Negativos de IAM e capability; CAS/fence stale; atomicidade audit/history/receipt; replay idempotente; commit indeterminado reconciliado; privacidade e ACL; API compatível; todos bypasses do scope bloqueados; publicação/snapshot sem partial; gerações/leitores consistentes; progresso/tentativas preservados; regressões adequadas; rollback ensaiado. Os tipos de evidência (unit, persistente, concorrência, integração, operacional) são discriminados na [matriz de readiness](editorial-generations-phase-2-1a-12c15-readiness-gates.md).

## Primeira onda

A C14 concluiu **PRIMEIRA ONDA NÃO SELECIONÁVEL COM AS EVIDÊNCIAS ATUAIS**. A C15 preserva esse bloqueio: não há escopo de mutação isolável com call graph/operator inventory e containment completo. Pode-se produzir novo estudo de fechamento após decisões e baseline, mas esta especificação não converte preparação documental em autorização.
