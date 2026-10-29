# Beta 7 — cobertura curricular por unidade

## Proveniência

A entrada do lote foi copiada em modo leitura da worktree de migração no commit `147dc68b81169f66b0ba3802fa2f26e5130923a3`, limpa nos caminhos curriculares selecionados. O runner validou os 221 artefatos listados no manifesto Beta 4 contra seus SHA-256 e também conferiu o hash da fonte 1.1 (`db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4`). Nenhuma fonte foi alterada. As unidades continuam identificadas como `rascunho`; autorização limitada a experimento isolado.

## Inventário verificado

| Unidade | Tópicos | Segmentos | Questões | Exercícios manuais | Referências | Relações | Materiais projeto |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1.1 — Computação e software | 5 | 8 | 5 | 3 | 2 | 3 | 0 |
| 1.2 — Ambiente de desenvolvimento | 5 | 5 | 5 | 3 | 3 | 3 | 0 |
| 2.1 — Terminal e navegação | 4 | 4 | 5 | 3 | 4 | 2 | 0 |
| 2.2 — Sistema e operação | 3 | 3 | 5 | 3 | 4 | 4 | 0 |
| 2.3 — Acesso remoto | 3 | 3 | 5 | 3 | 3 | 5 | 0 |
| 3.1 — Git local | 2 | 5 | 5 | 3 | 5 | 2 | 0 |
| 3.2 — Trabalho com histórico | 2 | 3 | 5 | 3 | 6 | 2 | 0 |
| 3.3 — GitHub | 4 | 4 | 5 | 3 | 7 | 4 | 0 |
| 3.4 — Revisita contínua | 1 | 3 | 4 | 2 | 2 | 2 | 0 |
| 3.5 — Projeto incremental da fase | 1 | 4 | 0 | 0 | 3 | 3 | 11 |
| **Total** | **30** | **42** | **44** | **26** | **39** | **30** | **11** |

As contagens vêm do manifesto curricular efetivo e foram conferidas novamente pelo conversor Beta 4 dentro do runner. O manifesto reporta 30 relações extraídas; o schema/importador persistiu 21 relações no cenário testado. As 9 restantes não devem ser tratadas como relações operacionais disponíveis.

## Estado da validação por unidade

| Unidade | Fonte/hash e conversão | Persistência e leitura por serviço/HTTP | Leitura de aluno e renderização real | Quiz/exercício por aluno | Critérios e conclusão | Estado Beta 7 |
|---|---|---|---|---|---|---|
| 1.1 | VERIFIED | VERIFIED — draft privado, estrutura preservada | NOT_VERIFIED — aluno corretamente recebe 404 | PARTIAL — fluxo exercitado em fixture sintética equivalente | PARTIAL — preservação, sem semântica automática completa | PARTIAL |
| 1.2 | VERIFIED | VERIFIED — draft privado, estrutura preservada | NOT_VERIFIED — aluno corretamente recebe 404 | PARTIAL — fluxo exercitado em fixture sintética equivalente | PARTIAL | PARTIAL |
| 2.1 | VERIFIED | VERIFIED — draft privado, estrutura preservada | NOT_VERIFIED — aluno corretamente recebe 404 | PARTIAL — fluxo exercitado em fixture sintética equivalente | PARTIAL | PARTIAL |
| 2.2 | VERIFIED | VERIFIED — draft privado, estrutura preservada | NOT_VERIFIED — aluno corretamente recebe 404 | PARTIAL — fluxo exercitado em fixture sintética equivalente | PARTIAL | PARTIAL |
| 2.3 | VERIFIED | VERIFIED — draft privado, estrutura preservada | NOT_VERIFIED — aluno corretamente recebe 404 | PARTIAL — fluxo exercitado em fixture sintética equivalente | PARTIAL | PARTIAL |
| 3.1 | VERIFIED | VERIFIED — draft privado, estrutura preservada | NOT_VERIFIED — aluno corretamente recebe 404 | PARTIAL — fluxo exercitado em fixture sintética equivalente | PARTIAL | PARTIAL |
| 3.2 | VERIFIED | VERIFIED — draft privado, estrutura preservada | NOT_VERIFIED — aluno corretamente recebe 404 | PARTIAL — fluxo exercitado em fixture sintética equivalente | PARTIAL | PARTIAL |
| 3.3 | VERIFIED | VERIFIED — draft privado, estrutura preservada | NOT_VERIFIED — aluno corretamente recebe 404 | PARTIAL — fluxo exercitado em fixture sintética equivalente | PARTIAL | PARTIAL |
| 3.4 | VERIFIED | VERIFIED — draft privado, estrutura preservada | NOT_VERIFIED — aluno corretamente recebe 404 | PARTIAL — amostra não percorreu seu quiz/exercícios no browser | PARTIAL | PARTIAL |
| 3.5 | VERIFIED | PARTIAL — conteúdo convertido; 11 materiais tipados no manifesto, sem fluxo de avaliação | BLOCKED — brief/checklists/marcos não passaram pela UI real do aluno | NOT_VERIFIED — não há quiz nem exercício no manifesto | BLOCKED — avaliação do projeto não implementada | PARTIAL |

`VERIFIED` em conversão e leitura significa apenas que os dados foram convertidos, persistidos em MongoDB descartável e lidos por `get_track_tree`/`get_node` e rotas reais com usuário administrativo. Não significa que o rascunho foi liberado ao aluno. O aluno foi negado para trilha e nó privados.

## Prova de lote

O teste `test_beta7_first_phase_http.py` executou dry-run, `run_import` real, contagens persistidas, consulta da árvore e de todos os 44 nós, contagens agregadas de 42 blocos teóricos, 44 blocos de quiz e 26 exercícios, replay idempotente sem duplicação, uma entrada de auditoria e zero registros de publicação. A fixture curricular ficou em estado draft/private.

O Playwright da Beta 7 percorreu **duas unidades sintéticas**, não as dez unidades revisadas. Portanto há cobertura estrutural do lote completo, mas a jornada do aluno no browser é amostral e sintética.

## Projeto 3.5

O inventário contém 11 artefatos (brief, quatro marcos, cinco checklists e rubrica); os dados privados permanecem classificados no manifesto/conversor. A avaliação e a liberação progressiva dos materiais não foram implementadas. O aluno não deve ser considerado capaz de concluir a fase enquanto esses critérios obrigatórios não tiverem contrato executável e apresentação revisada.

## Veredito da Frente B

**PRIMEIRA FASE CURRICULAR PARCIALMENTE VALIDADA — RECURSOS PENDENTES.** A conversão e a leitura administrativa integral passaram; navegação estudantil real pelas dez unidades, critérios executáveis e avaliação do projeto 3.5 não foram comprovados.
