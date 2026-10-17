# Relatório de execução

**Data:** 17/10/2026 (America/Sao_Paulo)  
**Início observado:** 07:55:22 UTC  
**Última atualização:** 09:17 UTC; PR #12 CI #70 concluída

## Resumo

Foram abertas alterações para isolamento/CI, otimização de ícones, visibilidade, E2E, validação de import, autorização baseada em role e importação persistente. PRs #9–#11 passaram CI; #13 passou CI #48 e revisão independente; #14 passou CI #46; #15 passou CI #59. PR #12 CI #51 passou backend/frontend/E2E e manteve os deploys manuais pulados. PR #12 também passou CI #60 (submissão de exercício) e CI #70 (prévia sem mutação, importação persistida e edição de nó após reload). A revisão independente do último fluxo não encontrou achados acionáveis. Nenhum PR foi mesclado.

## Alterações e evidências

- [#9 — fixtures Mongo e Compose](https://github.com/Saitar0/trilhacodeprod/pull/9): URI de testes validada para alvo descartável/loopback; validação de compose sem subir serviços. CI #18 passou backend/frontend/Compose.
- [#10 — ícones sob demanda](https://github.com/Saitar0/trilhacodeprod/pull/10): chunk Lucide de 799.578 B / 147,81 KiB gzip para 213.071 B / 50,78 KiB gzip (~65,7% de redução gzip). CI #19 passou. ~1.593 chunks pequenos sob demanda (~1,35 MB bruto total).
- [#11 — visibilidade direta de trilha](https://github.com/Saitar0/trilhacodeprod/pull/11): estudante recebe negação para metadados/árvore de trilhas privadas; CI #21 e revisão independente passaram.
- [#12 — E2E e gate de deploy](https://github.com/Saitar0/trilhacodeprod/pull/12): CI usa Mongo efêmero/seed fictício. CI #45 cobriu progresso do aluno, navegação admin e overflow em 360/390 px; CI #50 confirmou persistência da descrição após reload; CI #51 passou com ambos os deploys pulados. CI #60 passou envio e persistência de exercício com estudante/bloco temporários. CI #70 passou o fluxo admin de prévia, ausência de gravação antes do apply, importação persistida e edição do tópico com persistência após reload; revisão independente aprovada.
- [#13 — validação de import](https://github.com/Saitar0/trilhacodeprod/pull/13): rejeita estruturas/valores inválidos com 422 antes do planejamento; testa profundidade, int64, BSON NUL/UTF-8/tipos e limite conservador nos documentos gerados, incluindo slug/ref, tag e ref combinado de bloco. Local: 33 testes unitários e Ruff passaram; CI #48 backend/frontend/build/auditoria passou; revisor independente aprovou.
- [#14 — role refresh](https://github.com/Saitar0/trilhacodeprod/pull/14): teste de integração comprova que sessão existente ganha/perde permissão após mudança de role. CI #46 backend/frontend passou usando fixture Mongo descartável.
- [#15 — import persistente/idempotente](https://github.com/Saitar0/trilhacodeprod/pull/15): testa dry-run sem escrita, import real, árvore resultante e reimport idempotente. Revisor solicitou comprovação explícita de não mutação no dry-run; foi adicionada a expectativa de duas criações no primeiro import. CI #59 backend/frontend passou; execução está isolada pela fixture descartável.
- [#8 — registros de equipe](https://github.com/Saitar0/trilhacodeprod/pull/8): contém TEAM, roadmap, missão, decisões e este relatório.

## Percentual do escopo verificável

16 de 18 tarefas selecionadas foram concluídas (89%): 2 de qualidade/CI, 5 de jornadas E2E, overflow mobile, desempenho, 4 de backend/segurança e 3 de homologação funcional. Permanecem 1 tarefa de inspeção visual/teclado/acessibilidade local e 1 homologação operacional de staging bloqueada por gates e validação de host key.

## Testes

- Backend unitários locais: `python -m pytest unit_tests -q` — 33 passaram; Ruff nos arquivos do PR #13 passou.
- Backend de integração: PR #14 CI #46 e PR #15 CI #59 passaram em DB descartável. Não executados contra banco local/persistente.
- Frontend: Vitest 9/9; typecheck, lint, Playwright discovery e ESLint das specs/config passaram localmente para o conjunto anterior de E2E.
- CI: #18 PR #9 verde; #19 PR #10 verde; #21 PR #11 verde; #45/#50/#51/#60/#70 PR #12 verde; #48 PR #13 verde; #46 PR #14 verde; #59 PR #15 verde. No #70, backend, frontend e E2E passaram; deploy staging e produção foram pulados.
- Docker/browser E2E não foi executado localmente; a CI usa serviço Mongo isolado. Nenhum Mongo local foi iniciado.

## Revisão, segurança e limites

Revisão independente: #11 aprovado; #13 teve correções para hierarquia e limites BSON em node/tag/ref/block metadata e foi aprovado após revisão. #12 teve a corrida entre salvar e recarregar corrigida; CI confirmou persistência de edição. A revisão independente do E2E de edição de nó/import não encontrou achados acionáveis. #15 recebeu observação P2 sobre dry-run; a asserção de primeira criação foi adicionada antes da CI #59.

Nenhuma credencial/secret consultada ou registrada; nenhum Mongo real, migração, seed real, deploy, webhook, Coolify, VPS, SSH/firewall ou Dev Forge tocado. O erro anterior Host key verification failed não pôde ser validado com evidência pública segura. Arquivos locais preexistentes do usuário não foram incluídos nos PRs.

## PRs

- [#8 — registros da equipe](https://github.com/Saitar0/trilhacodeprod/pull/8) — aberto; documentação atualizada.
- [#9 — isolamento Mongo/Compose](https://github.com/Saitar0/trilhacodeprod/pull/9) — aberto; CI passou.
- [#10 — lazy icons](https://github.com/Saitar0/trilhacodeprod/pull/10) — aberto; CI passou.
- [#11 — visibilidade](https://github.com/Saitar0/trilhacodeprod/pull/11) — aberto; CI/review passaram.
- [#12 — E2E e gate de deploy](https://github.com/Saitar0/trilhacodeprod/pull/12) — aberto; CI #70 passou (inclui os fluxos acrescentados após #60); deploys foram pulados.
- [#13 — import validation](https://github.com/Saitar0/trilhacodeprod/pull/13) — aberto; CI #48 passou.
- [#14 — role revocation](https://github.com/Saitar0/trilhacodeprod/pull/14) — aberto; CI #46 passou.
- [#15 — import persistence](https://github.com/Saitar0/trilhacodeprod/pull/15) — aberto; CI #59 passou.
- [#16 — E2E submission](https://github.com/Saitar0/trilhacodeprod/pull/16) — fechado sem merge, substituído pelo commit no PR #12 para que o teste execute no workflow configurado para PRs contra main.

## Próxima retomada

Homologação visual/teclado e histórico permanecem para outra rodada com navegador/QA disponível. O host key do preflight G2 precisa ser comparado pelo operador com a fingerprint pública e a configuração conhecida, sem expor/alterar credenciais nesta missão. Gates operacionais G3–G6 continuam sem execução e dependem de aprovação.
