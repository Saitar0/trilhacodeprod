# Missão — avanço do roadmap técnico

**Data:** 17/10/2026 (America/Sao_Paulo)  
**Base:** main, 27a98964d55b96003fac70154178c5892da8d453  
**Branch de registros:** codex/ai-team-mission-2026-10-17

## Escopo

Avançar confiabilidade, E2E, responsividade, desempenho, segurança/integridade e preparação de homologação somente com problemas evidenciados e validações seguras. A matriz atual e o backlog estão em ROADMAP.md.

## Estado

- A — isolamento Mongo dos testes e validação Compose: CONCLUÍDA em PR #9; CI #18 verde.
- B — login/progresso do aluno, navegação/admin e persistência de edição: implementados no PR #12; CI #45, #50 e #51 passaram. O último CI também confirmou que E2E é requisito dos deploy jobs, que foram pulados. Um fluxo de submissão de exercício com aluno temporário foi adicionado ao PR #12 e aguarda CI #60/revisão.
- C — overflow horizontal nos breakpoints 360/390 px: CONCLUÍDA no escopo testado por CI #45; falta inspeção visual/teclado local.
- D — chunk de ícones sob demanda: CONCLUÍDA em PR #10; redução gzip medida de 65,7%, CI #19 verde.
- E — visibilidade privada (PR #11/CI #21), payload/tamanho BSON de import (PR #13, 33 testes locais, CI #48 e revisor aprovando) e role refresh/revogação (PR #14/CI #46): CONCLUÍDA para os achados atuais.
- F — homologação: PARCIAL. Edição admin persistiu em CI #50. Import de preview/persistência/idempotência passou em PR #15/CI #59; dry-run tem asserção de não mutação. Novo E2E de submissão aguarda CI #60. Edição de nó/bloco e outros fluxos ainda pendentes.
- G — staging/release: BLOQUEADA por gates operacionais. Nenhum acesso a Mongo real, segredo, SSH/Coolify/VPS ou operação G3–G6.

## Segurança e continuidade

CI de E2E usa Mongo sem volume persistente e DB trilhacode_e2e na própria job; backend de integração usa fixture de banco descartável. O novo caso cria estudante e bloco temporários, e remove o bloco no teardown do teste; a job destrói o banco ao final. Credenciais são de teste. As alterações locais anteriores do usuário foram preservadas e não incluídas nos PRs. PRs são para revisão manual; não houve merge/deploy.

## Critério de fechamento

A missão técnica fica PARCIAL até a CI/revisão do fluxo de submissão e os itens de homologação viáveis serem concluídos. Os gates de staging dependem do operador e de aprovação específica.
