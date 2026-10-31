# Roadmap técnico

## Atualização — integração progressiva Beta 1–9

- PR #39 contém a primeira onda contract-only da Beta 5, baseada na branch de fundação do PR #38, sem merge automático.
- O workflow `41082490518` passou integralmente no SHA `57f42bc1f20079afa815bdddd04e9e94531dbb5d`.
- Beta 1–9 foram reconstruídas; Beta 9 permanece branch-only e bloqueada por ausência de relatório/CI verificável.
- Relatório consolidado: `docs/ai-team/beta-integration-progressive-report.md`.

## Atualização — recuperação da fundação concluída

- A branch `codex/foundation-ci-e2e-recovery` foi validada no commit `bd8cd204857bbc581d5d6137ab6325d4022e13d7`.
- O workflow isolado `41080651996` passou Backend/MongoDB, Frontend, Docker/G2, Playwright E2E e resumo de homologação; deploys foram pulados.
- O PR #38 permanece aberto para revisão e merge manual.
- Beta 1–9, migração curricular, C14–C16, writers editoriais e ADR-008 continuam fora da integração e bloqueados conforme os gates existentes.
- Relatório: `docs/ai-team/foundation-validation-recovery-report.md`.

Atualizado em 17/10/2026 a partir de main (`5e503aecccfb85bd764d7af8e120d70819c6af4f`) e evidências de CI, revisão estática e terminal administrativo somente leitura.

## 18/10/2026 — G2-FIX em revisão

- Branch `codex/g2-fix` parte da main confirmada `2e83571af259ae2452994d81acb169f19a0e3a20`.
- Implementação proposta: validação de destino Mongo antes do cliente, incluindo `directConnection=true`; protocolo JSON versionado com manifesto independente; checks somente leitura com limite de agregação; runner fail-closed, sanitizado, com limpeza e lock seguros; guarda de `refs/heads/main`; documentação de implantação separada.
- PR #22 aberto para revisão; CI #39093646423 passou backend, frontend, Compose e Playwright E2E. Deploys foram pulados. A revisão independente final não encontrou achados P1 de falso sucesso/vazamento.
- Esta branch ainda não foi integrada. O G2 e os workflows de publicação de imagem não foram executados. Ativação requer nova imagem imutável compatível, revisão e implantação autorizada do runner/manifesto/rede na VPS.

| Frente | Status | Evidência verificada | Próximo critério |
| --- | --- | --- | --- |
| A — qualidade e confiabilidade | CONCLUÍDA | PR #9 adiciona Mongo descartável com URI local/direct-only e valida Compose sem iniciar serviços. CI #18 passou backend, frontend e Compose. | Revalidar após merge manual. |
| B — testes E2E | CONCLUÍDA NO ESCOPO SELECIONADO | PR #12 usa Mongo efêmero e seed de CI. CI #45 passou aluno, navegação admin e checks 360/390 px; #50 confirmou persistência da edição admin e #51 passou as dependências dos deploy jobs, que foram pulados. CI #60 passou submissão/persistência do aluno; CI #70 passou prévia sem mutação, importação persistida e edição de nó após reload. Revisor independente aprovou o fluxo de edição. | Ampliar cobertura para histórico/fluxos secundários em futura missão. |
| C — experiência/responsividade | CORRIGIDA E VALIDADA | Chromium local com API simulada verificou login, catálogo, conteúdo e exercício em desktop, 390 e 360 px; a lista admin e busca foram verificadas nas três larguras. Sem overflow; rodapé cobria resposta em 360/390 px e faltavam nomes acessíveis. PR #17; CI #39030010321 passou backend, frontend, Compose e Playwright E2E. | Ampliar inspeção para criação/importação admin e leitor de tela. |
| D — desempenho frontend | CONCLUÍDA | PR #10 reduziu chunk do catálogo Lucide de 799.578 B / 147,81 KiB gzip para 213.071 B / 50,78 KiB gzip (~65,7% menos no chunk). CI #19 passou. Build usa cerca de 1.593 chunks sob demanda (~1,35 MB bruto somado). | Monitorar requests e regressões do build após integração. |
| E — backend, segurança e integridade | CONCLUÍDA PARA OS ACHADOS DESTA MISSÃO | PR #11 fecha leituras diretas de trilhas privadas (CI #21). PR #13 valida formato/valores e tamanho BSON de documentos gerados antes do planejamento; 33 testes locais, CI #48 e revisão independente passaram. PR #14 prova promoção/revogação em sessão ativa; CI #46 passou. Auditoria de auth/CORS/proxy não encontrou falha adicional reproduzível. | Ampliar matriz para rotas menos cobertas em novo conjunto de testes de integração. |
| F — homologação funcional | PARCIAL | Edição de descrição em browser persistiu após reload na CI #50. PR #15 cobre dry-run sem mutação, import persistente e reimport idempotente; CI #59 passou. PR #12 cobre envio de exercício na UI e persistência (CI #60), além de prévia/importação e edição de nó com reload (CI #70). Não foi usado staging. | Cobrir histórico e executar homologação mais ampla somente em QA descartável. |
| G — staging e lançamento | BLOQUEADA POR COMPARAÇÃO DE IDENTIDADE E GATES OPERACIONAIS | G2 segue com `StrictHostKeyChecking=yes`, hostname configurado em secret e porta 22. O Web Console autenticado voltou a ficar disponível; `hostname -f` confirmou `srv2032201.hstgr.cloud` e a fingerprint foi calculada somente no console. Os valores dos secrets não são legíveis nesta sessão, portanto a comparação host/chave e a correção exata continuam pendentes. | Responsável compara privadamente a identidade configurada e a fingerprint, corrige somente o campo comprovadamente divergente com aprovação específica; despacho G2 exige aprovação separada. Não rodar G2, migração, seed ou deploy nesta etapa. |

## Backlog

- Concluído nesta missão: E2E de submissão e edição de nó/bloco via importação, em PR #12/CI #70.
- Histórico administrativo pela UI coberto no PR #18, CI #39035017901.
- Acessibilidade de importação admin com axe e teclado está no PR #19; CI #39037180408 passou em frontend, backend, Compose e E2E.
- Baseline de bundle medido na CI #39036366799; acompanhar o número de chunks e medir requests em runtime antes de definir budgets.
- Administrador da VPS valida fingerprint ED25519 pela fonte local confiável, confere host secret e corrige `G2_STAGING_SSH_HOST`/`G2_STAGING_SSH_KNOWN_HOSTS`; a alteração de secret exige aprovação do responsável.
- Retomar homologação G0–G7 somente sob aprovações e dados isolados exigidos nos runbooks.

## Salvaguardas

Nenhuma escrita ou operação em Mongo real, migration, seed real, backup/restore, deploy, Coolify, serviços da VPS, SSH remoto, secrets ou Dev Forge. O Web Console da VPS foi acessado somente para `hostname -f` e fingerprint SSH read-only. PRs aguardam integração manual.


## Atualização de retomada — 17/10/2026

- `main` avançou até `217f40fd3581f54eaa5f00546f643cc7203e1c72` (PRs #8–#15 e #17 integrados; PR #16 foi encerrado como supersedido pelo #12). A CI #39030667018 passou backend, frontend, Compose e Playwright E2E; deploys staging e produção foram pulados.
- PR #18 amplia o E2E do histórico administrativo: publica uma versão pela UI, edita a trilha depois e compara snapshot e estado atual no Mongo efêmero. CI #39035017901 passou backend, frontend, Compose e E2E; deploys foram pulados. Revisão independente sem achados acionáveis após ajuste do runbook G2.
- G2: Hostinger autenticada confirma VPS `srv2032201.hstgr.cloud` (`179.236.240.176`) em atividade. O botão Web Console aparece desabilitado. Coolify responde; `trilhacode-staging-api` está `exited:unhealthy`, Mongo staging está saudável. O comando SSH do workflow usa a porta 22 por padrão; o hostname configurado continua oculto no secret. Não há fingerprint autenticada disponível para comparar.
- A correção de `G2_STAGING_SSH_HOST`/`G2_STAGING_SSH_KNOWN_HOSTS` permanece pendente. Não alterar secrets, disparar G2, operar Mongo, migrar, criar índices, seed ou deploy sem aprovações correspondentes.


## Checkpoint de homologação e lançamento — 17/10/2026

- Base atual confirmada por busca de commits: `main` em `5e503aecccfb85bd764d7af8e120d70819c6af4f`; nenhum commit posterior foi encontrado. PR #18 está integrado.
- CI pós-merge #39036366799 passou em frontend, backend, Compose e E2E. Deploy de staging e produção foram pulados.
- PR #19: label acessível no JSON de importação, scan axe WCAG 2.1 A/AA na região do formulário e fluxo de teclado; revisão independente aprovada; CI #39037180408 passou frontend, backend, Compose e E2E; deploys staging/produção foram pulados.
- PR #20: cobre reenvio de resposta já enviada e persistência após reload em Mongo descartável; revisão independente aprovada; CI #39037237806 passou frontend, backend, Compose e E2E; deploys staging/produção foram pulados.
- Homologação descartável: importação, edição, publicação/histórico e envio de resposta cobertos pela CI anterior; PRs #19/#20 aumentam os fluxos. Staging real não foi homologado.
- A Hostinger Web Console está disponível. O hostname consultado no console corresponde à VPS identificada. A fingerprint foi calculada no terminal autenticado; não foi copiada para repositório, issue ou registro compartilhado. Os secrets G2 de hostname e known_hosts não podem ser inspecionados, portanto ainda falta a comparação independente e não é possível decidir se host ou chave precisa de correção.
- Coolify 4.4.6: `trilhacode-staging-api` consta `exited:unhealthy`, sem container presente; Mongo de staging `running:healthy`. Nenhuma ação de ciclo de vida foi executada.
- Bundle build da CI #39036366799: 1.611 arquivos JavaScript em `dist/assets`; 1.867,01 kB bruto somado (874,12 kB gzip se todos fossem baixados). O entry `index` tem 493,75 kB (159,36 kB gzip); `IconCatalog` tem 213,07 kB (50,83 kB gzip). O build levou 11,75 s. Esses valores descrevem o build, não requests carregadas em uma rota real; não foi aplicada otimização. Contagem de requests em runtime segue pendente.
- Próxima retomada: PRs #19 e #20 estão revisadas e com CI verde, prontas para integração manual. A PR #21 documenta este checkpoint. Manter as branches abertas e não fazer merge automático. Para G2, responsável compara em canal privado host, porta 22 e fingerprint com `G2_STAGING_SSH_KNOWN_HOSTS`; nenhuma secret ou workflow deve ser alterado/acionado sem aprovação específica.

## 26/10/2026 — Fase 1.2: notas e progresso confiáveis

- Implementação isolada na branch `codex/fase1-2-persistencia`, baseada no commit aprovado da Fase 1.1 `d2824aa6b910f747a29cbbbf8a2f123a5ad51d5c`.
- Concluídos localmente: versionamento/conflito de notas, recuperação em memória de rascunhos pendentes, barreira de navegação, CAS de progresso, eventos com outbox reconciliável, retries idempotentes e identificador explícito de tentativa de quiz.
- Validação local: pytest 112/112, Vitest 21/21, Ruff, typecheck, ESLint e build passaram. E2E não executado sem ambiente de aplicação e conta descartáveis preconfigurados.
- Não houve integração, push ou deploy. O conteúdo editorial permaneceu excluído da worktree.