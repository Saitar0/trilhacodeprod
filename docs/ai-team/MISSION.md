# Missão — avanço do roadmap técnico

## G2-FIX — endurecimento de software (18/10/2026)

- **Base:** `main` em `2e83571af259ae2452994d81acb169f19a0e3a20`; branch `codex/g2-fix`.
- **Escopo autorizado:** software G2, testes locais/CI e PR. Sem merge, deploy, G2, publicação de imagem, acesso ou alteração da VPS, banco staging, secrets, Coolify ou Dev Forge.
- **Implementação submetida:** URI restrita por parser PyMongo + parsing estrutural; `directConnection=true`; verificação de host/porta/db; protocolo versionado com IDs estáveis e manifesto; estados `OK`, `AUSENTE`, `CONFLITO`, `DUPLICATAS`; agregação limitada; classificação de falhas; saída sanitizada; lock host; workflow manual somente em `main`; documentação de implantação separada.
- **Bloqueio operacional conhecido:** runner referencia digest antigo que não contém o novo módulo. Nova imagem deve ser construída, revisada, publicada e pinada por procedimento posterior autorizado; a branch não dispara esses workflows.
- **PR:** [#22](https://github.com/Saitar0/trilhacodeprod/pull/22), aberto contra `main`, head `dd010fa243a5e8dc40b0a6b4f8948312f63c2ca8` no checkpoint. CI #39093646423 passou backend, frontend, Compose e Playwright E2E; deploys staging/produção foram pulados. Revisão independente final sem achados P1 de falso sucesso/vazamento.
- **Próximo passo:** revisão e merge manuais do PR. A aprovação do PR não autoriza ativação/G2; imagem compatível, rollout VPS e execução G2 permanecem separados. Não despachar G2.

## Retomada QA visual/acessibilidade + diagnóstico G2

**Data:** 17/10/2026

**Base:** `main` em `8dea1233d6977cbaf387dd5e0bb964f9464b3d9c`

**Branch de código:** `codex/qa-mobile-a11y`; [PR #17](https://github.com/Saitar0/trilhacodeprod/pull/17) aberto; CI #39030010321 passou backend, frontend, Compose e Playwright E2E. Deploys de staging e produção foram pulados.

- **QA de navegador:** CONCLUÍDA PARA OS FLUXOS COBERTOS. Chromium local com API simulada; login/catálogo/leitor/exercício e busca/lista admin em viewports 1280, 390 e 360 px. Tab levou o foco de Email para Senha e o indicador verde de foco foi confirmado. Sem overflow horizontal.
- **Correções:** CONCLUÍDAS LOCALMENTE. Rodapé sticky cobria o textarea de exercício em 360 e 390 px; labels de resposta/código e nomes de botões admin estavam ausentes. Ajustes e regressões E2E adicionados.
- **Validação:** typecheck, lint, build, Vitest (9/9), ESLint das specs E2E e descoberta Playwright passaram. Revisão independente aprovou a correção do seletor e o payload de desafio prático; CI #39030010321 passou backend, frontend, Compose e E2E em Mongo descartável. Deploys foram pulados.
- **G2:** DIAGNÓSTICO PARCIAL. O run anterior não conhece host ED25519; workflow preserva `StrictHostKeyChecking=yes`. A identidade precisa ser comparada com fingerprint administrada na VPS, indisponível neste ambiente. Nenhuma secret alterada e nenhum preflight/migração/seed/deploy executado.
- **Estado desta retomada:** PARCIALMENTE CONCLUÍDA, aguardando CI do PR e validação autenticada da fingerprint pelo administrador da VPS. Próxima ação permitida sem novo risco: acompanhar CI/revisão do PR. Próxima ação operacional requer aprovação do dono da infraestrutura para corrigir `G2_STAGING_SSH_HOST` e/ou `G2_STAGING_SSH_KNOWN_HOSTS` após comparação independente.

**Data:** 17/10/2026 (America/Sao_Paulo)  
**Base:** main, 27a98964d55b96003fac70154178c5892da8d453  
**Branch de registros:** codex/ai-team-mission-2026-10-17

## Escopo

Avançar confiabilidade, E2E, responsividade, desempenho, segurança/integridade e preparação de homologação somente com problemas evidenciados e validações seguras. A matriz atual e o backlog estão em ROADMAP.md.

## Estado

- A — isolamento Mongo dos testes e validação Compose: CONCLUÍDA em PR #9; CI #18 verde.
- B — login/progresso do aluno, navegação/admin e persistência de edição: implementados no PR #12; CI #45, #50 e #51 passaram. O último CI também confirmou que E2E é requisito dos deploy jobs, que foram pulados. CI #60 passou o fluxo de submissão com aluno temporário; CI #70 passou a prévia/importação persistida e edição de nó após reload, com aprovação independente.
- C — overflow horizontal nos breakpoints 360/390 px: CONCLUÍDA no escopo testado por CI #45; falta inspeção visual/teclado local.
- D — chunk de ícones sob demanda: CONCLUÍDA em PR #10; redução gzip medida de 65,7%, CI #19 verde.
- E — visibilidade privada (PR #11/CI #21), payload/tamanho BSON de import (PR #13, 33 testes locais, CI #48 e revisor aprovando) e role refresh/revogação (PR #14/CI #46): CONCLUÍDA para os achados atuais.
- F — homologação: PARCIAL. Edição admin persistiu em CI #50. Import de preview/persistência/idempotência passou em PR #15/CI #59; dry-run tem asserção de não mutação. PR #12/CI #60 passou envio de exercício e persistência; CI #70 passou importação UI e edição de nó após reload. Histórico e inspeção funcional mais ampla permanecem pendentes.
- G — staging/release: BLOQUEADA por gates operacionais. Nenhum acesso a Mongo real, segredo, SSH/Coolify/VPS ou operação G3–G6.

## Percentual do escopo verificável

16 de 18 tarefas selecionadas concluídas (89%); restam inspeção visual/teclado/acessibilidade local e homologação operacional de staging. A contagem usa tarefas verificáveis descritas em REPORT.md e não considera gates G3–G6 como execução autorizada.

## Segurança e continuidade

CI de E2E usa Mongo sem volume persistente e DB trilhacode_e2e na própria job; backend de integração usa fixture de banco descartável. O novo caso cria estudante e bloco temporários, e remove o bloco no teardown do teste; a job destrói o banco ao final. Credenciais são de teste. As alterações locais anteriores do usuário foram preservadas e não incluídas nos PRs. PRs são para revisão manual; não houve merge/deploy.

## Critério de fechamento

A missão permanece PARCIAL: as frentes técnicas selecionadas concluíram e passaram suas CI/revisões; a inspeção visual/teclado local e a homologação real de staging não puderam ser executadas com segurança/recursos disponíveis. Gates operacionais dependem do operador e de aprovação específica.


## Atualização de retomada — 17/10/2026

- Base remota confirmada: `main` em `217f40fd3581f54eaa5f00546f643cc7203e1c72`; PR #17 está integrado. CI #39030667018 passou backend, frontend, Compose e Playwright E2E; deploys foram pulados.
- QA de histórico implementado no PR #18: teste Playwright publica versão com nota única, edita a descrição e compara com o estado atual usando Mongo descartável da CI. CI #39035017901 passou backend, frontend, Compose e E2E; deploys foram pulados. Revisão independente não encontrou achados acionáveis após corrigir o passo de obtenção da chave pública no runbook G2.
- Diagnóstico G2 atualizado: painel Hostinger autenticado confirma VPS ativa, mas Web Console está desabilitado. Coolify é acessível; app API de staging está `exited:unhealthy`, Mongo staging `running:healthy`. Workflow usa porta SSH 22; segredo do hostname e segredo `known_hosts` não são legíveis por este canal. Chave ED25519/fingerprint do servidor não foi obtida.
- Missão segue parcial. Nenhuma secret foi alterada, G2 foi executado, nem houve migração, criação de índices, seed, deploy ou acesso/escrita ao banco real.


## Missão de homologação e preparação de lançamento — 17/10/2026

**Base confirmada:** `main` em `5e503aecccfb85bd764d7af8e120d70819c6af4f`, PR #18 integrado. CI pós-merge #39036366799 verde em backend, frontend, Compose e E2E; deploys pulados.

### Qualidade de código

- Histórico administrativo via UI coberto pelo PR #18 e CI #39035017901.
- Acessibilidade do formulário de importação está em PR #19: label, axe WCAG 2.1 A/AA e foco/Enter. Revisão independente aprovada; CI #39037180408 passou frontend, backend, Compose e E2E.
- Reenvio da resposta do aluno está em PR #20, com revisão independente aprovada; CI #39037237806 passou frontend, backend, Compose e E2E; deploys foram pulados.

### Homologação descartável

- CI #39036366799 confirmou as suites E2E anteriores em Mongo descartável.
- Importação com preview, persistência, edição e histórico publicado já têm cobertura de UI na CI; PR #20 acrescenta atualização após envio e persistência.
- Execução local mutável foi evitada porque a configuração de Mongo local não foi demonstrada como descartável. CI #39037180408 e #39037237806 passaram em Mongo descartável; deploys foram pulados.

### Pendências de staging

- API `trilhacode-staging-api` continua `exited:unhealthy`, sem container presente; Mongo de staging responde como healthy.
- A sessão autenticada da Hostinger agora mostra o Web Console. Hostname e fingerprint foram consultados com comandos de leitura, mas a fingerprint não foi copiada para este registro.
- O hostname e a chave conhecida do GitHub são secrets não inspecionáveis pela sessão; responsável precisa compará-los privadamente antes de se determinar a correção.

### Bloqueios que exigem autorização

- Alterar `G2_STAGING_SSH_HOST` ou `G2_STAGING_SSH_KNOWN_HOSTS`, ou despachar G2, depende de autorização específica. G2 consulta Mongo staging.
- Migração, criação de índices, seed, backup/restore, deploy, mudança em serviços/credenciais/redes VPS ou Dev Forge não foram autorizados nem executados.
- Os testes automatizados não representam homologação visual ou operacional de staging; não declarar produto pronto para produção.

### Instruções de retomada

1. PRs #19 e #20 passaram CI e revisão; manter prontas para integração manual sem merge automático.
2. Atualizar este checkpoint com os resultados finais e o status de PRs #19/#20; não fazer merge.
3. Manter o baseline de performance até haver medição de requests em runtime.
4. O responsável compara em canal privado o hostname confirmado no Web Console, porta SSH 22 e fingerprint da chave ED25519 com os valores do GitHub; só após comparação e aprovação específica corrigir o secret comprovadamente divergente. A aprovação para G2 permanece separada.
