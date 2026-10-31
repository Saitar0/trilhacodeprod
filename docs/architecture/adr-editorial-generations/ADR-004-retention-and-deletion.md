# ADR-004 — Retenção, exclusão e recuperação

**Status:** Proposed
**Tipo:** política candidata; nenhum prazo ou regra de privacidade foi aprovado.
**Baseline analisado:** e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636.

## 1. Contexto

Uma geração pode ser referenciada por head ativo, sessões, tentativas, avaliações, histórico e restore. A exclusão atual de trilha remove dados relacionados em cascata; notas e submissões podem resolver títulos por IDs vivos. Evidência: audit B.2 seções 2-3; backend/services/tracks.py:98-115; backend/services/activities.py:130-190; backend/services/progress.py:152-379; backend/services/submissions.py:20-204; backend/learning.py:175-370; e5bf…; confiança alta para referências identificadas.

## 2. Problema

Retenção ilimitada eleva custo e risco de privacidade; remoção prematura pode tornar avaliação, progresso e auditoria irrecuperáveis.

## 3. Requisitos

- Nunca remover geração ativa ou referenciada por operação/sessão/tentativa/histórico obrigatório.
- Separar lifecycle do conteúdo editorial de dados pessoais e dados de aluno.
- Toda exclusão deve ser auditável, idempotente e recuperável quando aplicável.
- Nenhum prazo de retenção deve ser inventado nesta decisão técnica.

## 4. Alternativas

| Alternativa | Benefício | Custo/risco |
|---|---|---|
| A. Retenção ilimitada | Recuperação simples | Custo e obrigações de privacidade sem limite |
| B. Janela fixa | Operação previsível | Pode apagar referência necessária ou exceder obrigação |
| C. Por referência | Mantém somente gerações referenciadas | Precisa inventário confiável e GC concorrente segura |
| D. Política por curso | Alinha ao produto | Complexidade e regras inconsistentes |
| E. Híbrida: referências + obrigações + período de graça aprovado | Equilibra necessidade e descarte | Exige owners e avaliação legal/privacidade; sem política numérica ainda |

## 5. Critérios de avaliação

Recuperabilidade, referência completa, dados pessoais, custo, auditoria, tratamento de delete/restore e possibilidade de hold legal.

## 6. Recommended Decision

Recomenda-se E sem definir duração. O GC somente poderá marcar uma geração elegível após coletar referências conhecidas (head, sessões, tentativas, submissions, eventos/histórico, operations e versões). Deve aguardar período de graça que será decidido por produto/privacidade; antes da remoção, revalidar referência e ownership. Falta de índice ou referência desconhecida bloqueia remoção. Exclusão de conteúdo pode primeiro criar tombstone/retirada sem apagar dados de alunos.

## 7. Justificativa

O serviço atual faz cascata em dados vivos; a introdução de IDs imutáveis cria referências de longo prazo. Política de retenção é decisão de produto, privacidade e eventualmente jurídica, não resultado da PoC.

## 8. Consequências positivas

Evita geração órfã enquanto há uso; dá trilha auditável; permite retirada lógica antes da coleta física.

## 9. Consequências negativas

Requer indexar referências, operar candidatos de GC, observabilidade e custeio; material histórico pode crescer.

## 10. Riscos

Referência esquecida torna GC destrutivo. Tombstone sem prazo cria retenção indefinida. Dados pessoais incorporados no snapshot podem impedir política limpa de exclusão.

## 11. Impacto na migração

Antes de backfill, separar conteúdo pedagógico de PII/progresso/notas/submissions. Inventariar todos os consumidores e fixar uma tabela de retenção aprovada. Backfill não pode ativar head nem apagar origem.

## 12. Compatibilidade

Manter IDs usados por tentativas/progresso. Para conteúdo removido, responder conforme política de produto sem reutilizar IDs nem silently retarget links para outro conteúdo.

## 13. Estratégia de rollback

Pausar GC sem remover dados. Tombstone ou soft-delete pode ser revertido por operação auditada enquanto não houver obrigação de eliminação definitiva. Exclusão física acidental requer backup/restore controlado, não recriação improvisada.

## 14. Testes obrigatórios

Geração ativa/referenciada é inelegível; duas coletas concorrentes não removem referenciada; referência criada durante grace cancela remoção; órfãos reportados sem apagar aluno; tombstone e retenção auditados; purge tem prova de escopo e idempotência.

## 15. Critérios de aceitação

Todos os tipos de referência têm owner e índice/consulta; prazo aprovado; revisão de privacidade/legal quando aplicável; ensaio de GC com fakes e DB descartável; relatórios sem conteúdo sensível; rollback de parada demonstrado.

## 16. Decisões dependentes

ADR-002, ADR-003, ADR-006 e decisão de produto/privacidade sobre histórico, exclusão e urgência.

## 17. Perguntas para aprovação humana

Quais obrigações exigem manter versões de quiz/notas? Qual prazo para sessões inativas? Há direito de exclusão/anonimização aplicável? Quem aprova hard delete? Quais exceções legais e incident holds existem?

## 18. Approved Decision

Nenhuma. Não existe prazo de retenção aprovado nesta fase.

## 19. Evidência e confiança

Confirmado no código: delete_track remove coleções relacionadas; progress/submission/attempt usam chaves diferentes e históricos; e5bf…; backend/services/tracks.py:98-115, backend/services/progress.py:152-379, backend/services/submissions.py:20-204, backend/services/activities.py:130-190. Alta. Necessidade legal concreta não foi verificada; pendente de privacidade/jurídico.

## 20. Risco de implementação

GC não faz parte da primeira entrega de geração. Até decisão e inventário completo, preservar dados e desabilitar remoção física por geração.
