# Relatório de execução

## Checkpoint G2-FIX — 18/10/2026

- Branch isolada `codex/g2-fix`, baseada na `main` `2e83571af259ae2452994d81acb169f19a0e3a20`.
- Implementação inclui validador de URI antes da criação do cliente Mongo (host único, destino staging, porta, banco e `directConnection=true` obrigatório), protocolo de resultado versionado/manifesto, checks de metadados e agregações somente leitura com `maxTimeMS`, runner root fail-closed com lock e sem publicação de stdout/stderr bruto, workflow G2 protegido por ref e runbook atualizado.
- Testes adicionados para allow/deny URI, sem conexão antes da validação, relatório ausente/incompleto/duplicado/extra/malformado, semântica dos estados, categorias de falha, saída-canário e limpeza/interrupção.
- Revisão independente identificou digest de imagem incompatível, risco de discovery Mongo, corrida de limpeza em sinais, concorrência fora do Actions, lock path inseguro e ambiguidade do exit 137. Correções incluem `directConnection=true` obrigatório; diretório `/run/trilhacode-g2-preflight` validado sem links simbólicos (root:0700); arquivo de lock root:0600 e `flock`; teste real de duas invocações concorrentes; limpeza por nome aleatório/label; sinais HUP/INT/TERM; e categoria própria para 137. A limpeza interrompida sem confirmação agora termina como unverified/74. Re-revisão final solicitada.
- O digest antigo continua deliberadamente pinado na fonte; os workflows de build/publicação foram ajustados para usar exatamente o SHA selecionado, mas não foram executados. Nova publicação e alteração do pin exigem autorização operacional separada.
- Não houve acesso à Hostinger, execução G2, publicação de imagem, alteração de staging/produção/Dev Forge, segredo, banco, rede, Docker, deploy, migração, índice ou seed.
- Validação local: Python 3.13 `pytest unit_tests -q` — 68 passaram, 21 ignorados por dependências POSIX não disponíveis no Windows; `compileall` e `git diff --check` passaram. Ruff não está instalado localmente. A CI Ubuntu do PR é necessária para executar o harness bash/jq/flock.
- Retomada: rodar testes locais disponíveis, revisar relatório do revisor independente, completar validação da CI do PR e reportar limitações de ambiente Windows; abrir PR e aguardar aprovação/merge manual.

**Data:** 17/10/2026 (America/Sao_Paulo)  
**Início observado:** 07:55:22 UTC  
**Última atualização:** 09:17 UTC; PR #12 CI #70 concluída

## Retomada — QA visual/acessibilidade e diagnóstico G2 (base 8dea1233)

### QA de navegador

- Chromium local em `http://127.0.0.1:5173` com respostas de API e submissões simuladas; nenhuma chamada de backend real ou banco. Login/formulário, catálogo, navegação para conteúdo e exercício e envio foram verificados em 1280, 390 e 360 px; busca e lista admin, nas mesmas três larguras.
- Medida `documentElement.scrollWidth`/`body.scrollWidth`: igual à viewport em todos os fluxos registrados (sem overflow horizontal).
- Antes da correção, o retângulo do rodapé sobrepunha o campo de resposta em 390 px (interseção vertical 819–870 px) e 360 px (818–920 px versus campo até 933 px). Depois, o rodapé passou a seguir o fluxo em telas estreitas; interseção é falsa nas duas larguras. Em desktop (1280 px), o comportamento sticky continua.
- Antes, o textarea de resposta não tinha label associado; depois, Chromium reporta “Sua resposta para Exercício de resposta aberta”. Três botões admin (mover acima/abaixo e menu de ações) não tinham nome acessível; depois passaram a expor nomes por trilha.
- Teclado: tabulação de Email para Senha moveu foco corretamente e o alvo permaneceu visível; Chromium computou halo verde de foco `0 0 0 1px rgb(16, 183, 127)`. Inspeção manual com leitor de tela/axe não foi executada.
- Evidências temporárias de screenshot/resultados foram mantidas somente durante a análise no worktree; não são arquivos de produto. Regressões permanentes foram adicionadas às specs E2E existentes (serão executadas no CI, que usa Mongo descartável).

### Alterações deste PR

- Em exercícios abertos e desafios práticos, associar labels ocultos aos campos de resposta e código.
- Em leitores estreitos, remover o posicionamento sticky que cobria a resposta; manter sticky a partir de `sm`.
- Nomear os três botões somente com ícone em administração e especificar `type="button"` nos controles de ordem.
- E2E de submissão verifica labels acessíveis de resposta aberta e código prático, ausência de overflow e não sobreposição em 360/390 px; E2E admin verifica nomes acessíveis dos controles. Revisão independente confirmou o payload de criação, cleanup e seletores do cenário.
- Local: `npm run typecheck`, `npm run lint`, build, Vitest (9/9), ESLint das specs E2E, descoberta Playwright e QA Chromium com mocks passaram. O E2E integrado usa Mongo efêmero na CI; não foi iniciado Compose local por existirem containers/volumes QA antigos e outros serviços compartilhados no Docker.
- [PR #17 — correções mobile e acessibilidade](https://github.com/Saitar0/trilhacodeprod/pull/17), branch `codex/qa-mobile-a11y`. CI #39030010321 passou backend, frontend, Compose e Playwright E2E; deploys permaneceram pulados.

### Diagnóstico G2

- Run `39011425126`, SHA anterior: a etapa de configuração verificou presença das quatro secrets sem imprimir valores. A etapa SSH falhou com `No ED25519 host key is known for [host mascarado]` e `Host key verification failed`.
- O workflow lê `G2_STAGING_SSH_HOST`, `G2_STAGING_SSH_USER`, `G2_STAGING_SSH_KEY`, `G2_STAGING_SSH_KNOWN_HOSTS`, usa porta 22, `UserKnownHostsFile` temporário e `StrictHostKeyChecking=yes`, e chama somente `trilhacode-g2-preflight`.
- Evidência aponta host/alias sem entrada ED25519 correspondente no arquivo temporário ou uma entrada com formato/host incompatível. Não é o diagnóstico de chave alterada (`REMOTE HOST IDENTIFICATION HAS CHANGED`) e não prova rotação ou divergência criptográfica.
- Comparação solicitada não pôde ser concluída: os logs mascaram o hostname; o valor `known_hosts` é secret e inacessível; nenhum canal SSH autenticado ou fonte do administrador no servidor está disponível. A configuração versionada contém apenas nomes de secrets, não a chave/fingerprint.
- A correção permanece bloqueada até o administrador comparar a chave apresentada com `/etc/ssh/ssh_host_ed25519_key.pub` (ou outra fonte local confiável) e confirmar o hostname efetivo. Só então ele pode atualizar `G2_STAGING_SSH_HOST` e/ou `G2_STAGING_SSH_KNOWN_HOSTS`; aprovação do responsável da infraestrutura é necessária para alterar secrets. Não desativar verificação estrita nem confiar em `ssh-keyscan` sem verificação independente.
- Nenhum G2 preflight, migração, índice, seed, deploy, acesso a VPS/SSH/Coolify/Mongo real, alteração de secret ou operação Dev Forge ocorreu.

## Resumo

Foram abertas alterações para isolamento/CI, otimização de ícones, visibilidade, E2E, validação de import, autorização baseada em role e importação persistente. PRs #9–#11 passaram CI; #13 passou CI #48 e revisão independente; #14 passou CI #46; #15 passou CI #59. PR #12 CI #51 passou backend/frontend/E2E e manteve os deploys manuais pulados. PR #12 também passou CI #60 (submissão de exercício) e CI #70 (prévia sem mutação, importação persistida e edição de nó após reload). A revisão independente do último fluxo não encontrou achados acionáveis. No momento da conclusão original da missão, nenhum PR havia sido mesclado. **Atualização posterior:** os PRs #9–#15 foram integrados à `main` por squash; a execução integrada da CI sobre a `main` ainda precisa de validação explícita.

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
- [#9 — isolamento Mongo/Compose](https://github.com/Saitar0/trilhacodeprod/pull/9) — mesclado à `main`; CI passou.
- [#10 — lazy icons](https://github.com/Saitar0/trilhacodeprod/pull/10) — mesclado à `main`; CI passou.
- [#11 — visibilidade](https://github.com/Saitar0/trilhacodeprod/pull/11) — mesclado à `main`; CI/review passaram.
- [#12 — E2E e gate de deploy](https://github.com/Saitar0/trilhacodeprod/pull/12) — mesclado à `main`; CI #70 passou (inclui os fluxos acrescentados após #60); deploys foram pulados.
- [#13 — import validation](https://github.com/Saitar0/trilhacodeprod/pull/13) — mesclado à `main`; CI #48 passou.
- [#14 — role revocation](https://github.com/Saitar0/trilhacodeprod/pull/14) — mesclado à `main`; CI #46 passou.
- [#15 — import persistence](https://github.com/Saitar0/trilhacodeprod/pull/15) — mesclado à `main`; CI #59 passou.
- [#16 — E2E submission](https://github.com/Saitar0/trilhacodeprod/pull/16) — fechado sem merge, substituído pelo commit no PR #12 para que o teste execute no workflow configurado para PRs contra main.

## Atualização de integração

Os PRs #9, #11, #13, #14, #15, #12 e #10 foram mesclados nessa ordem, após revisão de seus patches e confirmação de CI verde nas branches. A CI sobre a combinação final em `main` ainda não foi confirmada nesta atualização. O PR #8 documenta a missão e este registro de integração.

## Próxima retomada

Homologação visual/teclado e histórico permanecem para outra rodada com navegador/QA disponível. O host key do preflight G2 precisa ser comparado pelo operador com a fingerprint pública e a configuração conhecida, sem expor/alterar credenciais nesta missão. Gates operacionais G3–G6 continuam sem execução e dependem de aprovação.


## Retomada — estado observado em 17/10/2026

### Repositório e CI

- GitHub confirma `main` em `217f40fd3581f54eaa5f00546f643cc7203e1c72`, correspondente ao merge do PR #17. Não foi encontrado commit posterior nos 10 commits mais recentes.
- CI #39030667018 concluiu com sucesso: `compose-config`, backend, frontend e E2E. Os jobs `deploy-staging` e `deploy-production` foram pulados.
- PRs #8–#15 e #17 foram encontrados integrados; PR #16 foi encerrado como supersedido pelo #12. PR #17 foi fechado por merge nesse SHA.
- Checkout local em `27a98964` está oito commits atrás e tem modificações e arquivos não rastreados. Foi preservado sem limpeza; clone remoto limpo não foi possível por bloqueio de DNS/rede do host.
- PR #18 adiciona um E2E que publica uma nota única, edita a descrição depois e verifica a nota e um diff positivo pela UI de versões no pipeline com Mongo efêmero. CI #39035017901 passou backend, frontend, Compose e E2E; deploys foram pulados. A revisão técnica independente aprovou o isolamento do teste e o runbook G2 depois do ajuste para obter a linha da chave pública e a fingerprint no canal administrativo.

### Diagnóstico G2 e infraestrutura

- Sessão autenticada Hostinger respondeu. VPS `srv2032201.hstgr.cloud` / `179.236.240.176`, Ubuntu 24.04 com Coolify, consta “Em atividade”; painel informa KVM 2, 2 vCPU/8 GB RAM/100 GB, validade até 03/11/2026.
- O Web Console está desabilitado no painel no momento da consulta; não foi possível consultar `/etc/ssh/ssh_host_ed25519_key.pub` por canal administrativo.
- Coolify 4.4.6 respondeu por conexão de leitura. `trilhacode-staging-api` (projeto Trilha Code) consta `exited:unhealthy` e sem container presente; `trilhacode-staging-mongodb` está `running:healthy`. Os apps do projeto `general` incluem Dev Forge; nenhum lifecycle ou dado deles foi acessado.
- `.github/workflows/g2-staging-preflight.yml` usa as secrets `G2_STAGING_SSH_*` e não define `-p`/`Port`; OpenSSH usa 22. O alvo de `G2_STAGING_SSH_HOST` e a entrada em `G2_STAGING_SSH_KNOWN_HOSTS` não podem ser lidos pelos canais disponíveis. A falha anterior é compatível com entrada ED25519 ausente/incompatível, mas não confirma host correto nem fingerprint.
- Nenhuma chave/fingerprint obtida. Não foram alteradas secrets/configurações, executado G2, acesso SSH, deploy, migração, índice, seed, backup/restore ou operação em Mongo.
- Bloqueio e retomada: quando o Web Console ficar disponível, administrador deve obter fingerprint SHA256 no próprio host e comparar em canal privado com hostname, porta 22 e entrada `known_hosts` configurados no GitHub. Corrigir secrets apenas depois dessa comparação e aprovação específica; executar G2 exige aprovação distinta.


## Relatório de homologação — 17/10/2026

### Código e qualidade

- PR #18 integrado em `5e503aecccfb85bd764d7af8e120d70819c6af4f`; a CI pós-merge #39036366799 passou backend, frontend, Compose e E2E. Deploys foram pulados.
- PR #19 adiciona label ao campo JSON de importação, axe-core WCAG 2.1 A/AA e verificação de Tab/Enter. Revisão independente aprovada; CI #39037180408 passou frontend, backend, Compose e E2E; deploys foram pulados.
- PR #20 testa a edição e o reenvio de uma resposta no estado enviado, e a persistência após reload. Revisão independente aprovada; CI #39037237806 passou frontend, backend, Compose e E2E; deploys foram pulados.
- Os dois E2Es mutáveis permanecem dentro dos jobs que criam `trilhacode_e2e` Mongo efêmero. Não foram executados localmente contra uma base não identificada.

### Performance de build

- Job frontend da CI #39036366799: 2.429 módulos transformados; build em 11,75 s.
- `dist/assets` contém 1.611 arquivos JavaScript, total bruto 1.867,01 kB; a soma gzip reportada é 874,12 kB se todos os chunks fossem solicitados.
- Chunk `index`: 493,75 kB bruto / 159,36 kB gzip. Chunk `IconCatalog`: 213,07 kB bruto / 50,83 kB gzip. Separação em chunks indica carregamento dinâmico, mas a CI não mediu quantos chunks uma rota baixa em runtime.
- Não há mudança de otimização proposta sem medição real de requests por rota; evitar reduzir o catálogo de ícones sem comprovar impacto funcional e ganho.

### Staging, G2 e bloqueios

- A sessão autenticada da Hostinger exibe o Web Console da VPS. Em modo somente leitura, `hostname -f` identificou `srv2032201.hstgr.cloud`; `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256` calculou a fingerprint no console. O valor não foi copiado para os arquivos do projeto.
- O workflow G2 usa SSH na porta 22 e exige `StrictHostKeyChecking=yes`. Os valores dos secrets configurados no GitHub não são acessíveis pela sessão; hostname/known_hosts esperados ainda precisam ser comparados privadamente pelo responsável. Não há base para decidir secret a corrigir.
- Coolify continua mostrando a API de staging como `exited:unhealthy`, sem container; Mongo está saudável. Isso não valida staging nem autoriza ciclo de vida.
- Nenhuma secret, G2, conexão SSH, banco real, migration, índice, seed, backup, deploy ou recurso Dev Forge foi alterado/acionado.
- `DEPLOY.md` possuía frase introdutória que contradizia sua sequência operacional de migração. A correção documental está incluída neste checkpoint para revisão.

