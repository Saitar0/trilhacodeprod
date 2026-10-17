# Missão — avanço do roadmap técnico

## Retomada QA visual/acessibilidade + diagnóstico G2

**Data:** 17/10/2026

**Base:** `main` em `8dea1233d6977cbaf387dd5e0bb964f9464b3d9c`

**Branch de código:** `codex/qa-mobile-a11y`

- **QA de navegador:** CONCLUÍDA PARA OS FLUXOS COBERTOS. Chromium local, API simulada, login/catálogo/leitor/exercício e listagem admin; viewports 1280, 390 e 360 px. Tab levou o foco de Email para Senha. Sem overflow horizontal.
- **Correções:** CONCLUÍDAS LOCALMENTE. Rodapé sticky cobria o textarea de exercício em 360 e 390 px; labels de resposta/código e nomes de botões admin estavam ausentes. Ajustes e regressões E2E adicionados.
- **Validação:** typecheck, lint, build, Vitest (9/9) e fluxo simulado passaram. A spec E2E que usa Mongo real descartável não foi executada localmente; CI do PR é a verificação final integrada.
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
