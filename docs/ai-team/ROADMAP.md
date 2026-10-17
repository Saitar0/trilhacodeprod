# Roadmap técnico

Atualizado em 17/10/2026 a partir de main (8dea1233) e evidências de CI e QA local isolado. Status distinguem validação local, CI e homologação real.

| Frente | Status | Evidência verificada | Próximo critério |
| --- | --- | --- | --- |
| A — qualidade e confiabilidade | CONCLUÍDA | PR #9 adiciona Mongo descartável com URI local/direct-only e valida Compose sem iniciar serviços. CI #18 passou backend, frontend e Compose. | Revalidar após merge manual. |
| B — testes E2E | CONCLUÍDA NO ESCOPO SELECIONADO | PR #12 usa Mongo efêmero e seed de CI. CI #45 passou aluno, navegação admin e checks 360/390 px; #50 confirmou persistência da edição admin e #51 passou as dependências dos deploy jobs, que foram pulados. CI #60 passou submissão/persistência do aluno; CI #70 passou prévia sem mutação, importação persistida e edição de nó após reload. Revisor independente aprovou o fluxo de edição. | Ampliar cobertura para histórico/fluxos secundários em futura missão. |
| C — experiência/responsividade | CORRIGIDA E VALIDADA | Chromium local com API simulada verificou login, catálogo, conteúdo e exercício em desktop, 390 e 360 px; a lista admin e busca foram verificadas nas três larguras. Sem overflow; rodapé cobria resposta em 360/390 px e faltavam nomes acessíveis. PR #17; CI #39030010321 passou backend, frontend, Compose e Playwright E2E. | Ampliar inspeção para criação/importação admin e leitor de tela. |
| D — desempenho frontend | CONCLUÍDA | PR #10 reduziu chunk do catálogo Lucide de 799.578 B / 147,81 KiB gzip para 213.071 B / 50,78 KiB gzip (~65,7% menos no chunk). CI #19 passou. Build usa cerca de 1.593 chunks sob demanda (~1,35 MB bruto somado). | Monitorar requests e regressões do build após integração. |
| E — backend, segurança e integridade | CONCLUÍDA PARA OS ACHADOS DESTA MISSÃO | PR #11 fecha leituras diretas de trilhas privadas (CI #21). PR #13 valida formato/valores e tamanho BSON de documentos gerados antes do planejamento; 33 testes locais, CI #48 e revisão independente passaram. PR #14 prova promoção/revogação em sessão ativa; CI #46 passou. Auditoria de auth/CORS/proxy não encontrou falha adicional reproduzível. | Ampliar matriz para rotas menos cobertas em novo conjunto de testes de integração. |
| F — homologação funcional | PARCIAL | Edição de descrição em browser persistiu após reload na CI #50. PR #15 cobre dry-run sem mutação, import persistente e reimport idempotente; CI #59 passou. PR #12 cobre envio de exercício na UI e persistência (CI #60), além de prévia/importação e edição de nó com reload (CI #70). Não foi usado staging. | Cobrir histórico e executar homologação mais ampla somente em QA descartável. |
| G — staging e lançamento | BLOQUEADA POR IDENTIDADE DO HOST E GATES OPERACIONAIS | Workflow #39011425126 parou no SSH fixo: log mascarado informa “No ED25519 host key is known for [host]” seguido de “Host key verification failed”. Isso aponta entrada ausente/incompatível no `known_hosts`, não prova rotação da chave. O workflow usa `StrictHostKeyChecking=yes`, host/porta 22 e secret `G2_STAGING_SSH_KNOWN_HOSTS`; não foi possível ler o host/secret nem obter fingerprint do arquivo público administrado na VPS. | Administrador confirma host e fingerprint ED25519 diretamente em `/etc/ssh/ssh_host_ed25519_key.pub` (ou fonte equivalente autenticada), compara com a entrada secret e corrige `G2_STAGING_SSH_HOST`/`G2_STAGING_SSH_KNOWN_HOSTS` só após validação. Não rodar G2 preflight, migração, seed ou deploy nesta etapa. |

## Backlog

- Concluído nesta missão: E2E de submissão e edição de nó/bloco via importação, em PR #12/CI #70.
- Cobrir histórico usando apenas banco QA descartável.
- Ampliar QA visual/acessibilidade para criação/importação admin, formulários e leitor de tela; considerar axe.
- Considerar budgets automáticos de bundle após estabilizar e observar a quantidade de chunks/requests.
- Administrador da VPS valida fingerprint ED25519 pela fonte local confiável, confere host secret e corrige `G2_STAGING_SSH_HOST`/`G2_STAGING_SSH_KNOWN_HOSTS`; a alteração de secret exige aprovação do responsável.
- Retomar homologação G0–G7 somente sob aprovações e dados isolados exigidos nos runbooks.

## Salvaguardas

Nenhum acesso ou escrita em Mongo real, migração, seed real, backup/restore, deploy, Coolify, VPS, SSH/firewall, secret ou Dev Forge. PRs permanecem abertos; nenhum merge automático.


## Atualização de retomada — 17/10/2026

- `main` avançou até `217f40fd3581f54eaa5f00546f643cc7203e1c72` (PRs #8–#15 e #17 integrados; PR #16 foi encerrado como supersedido pelo #12). A CI #39030667018 passou backend, frontend, Compose e Playwright E2E; deploys staging e produção foram pulados.
- PR #18 amplia o E2E do histórico administrativo: publica uma versão pela UI, edita a trilha depois e compara snapshot e estado atual no Mongo efêmero. CI #39035017901 passou backend, frontend, Compose e E2E; deploys foram pulados. Revisão independente sem achados acionáveis após ajuste do runbook G2.
- G2: Hostinger autenticada confirma VPS `srv2032201.hstgr.cloud` (`179.236.240.176`) em atividade. O botão Web Console aparece desabilitado. Coolify responde; `trilhacode-staging-api` está `exited:unhealthy`, Mongo staging está saudável. O comando SSH do workflow usa a porta 22 por padrão; o hostname configurado continua oculto no secret. Não há fingerprint autenticada disponível para comparar.
- A correção de `G2_STAGING_SSH_HOST`/`G2_STAGING_SSH_KNOWN_HOSTS` permanece pendente. Não alterar secrets, disparar G2, operar Mongo, migrar, criar índices, seed ou deploy sem aprovações correspondentes.
