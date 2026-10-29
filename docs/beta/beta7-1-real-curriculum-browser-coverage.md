# Beta 7.1 — cobertura do currículo revisado

## Proveniência

Fonte: worktree de migração, revisão `migration@147dc68:tracked-clean-first-phase-files`. Os arquivos curriculares selecionados estavam rastreados e limpos na inspeção somente leitura. Havia mudanças locais preexistentes em outros arquivos de documentação/conversão naquela worktree; foram preservadas e não entraram na cópia ou nos commits Beta 7.1. A execução copiou somente a fonte selecionada para o workspace temporário do runner e confirmou hashes antes da conversão. Classificação: `APPROVED_FOR_ISOLATED_EXPERIMENT`; o rascunho não está aprovado para publicação ou importação operacional.

Manifesto Beta 4: `docs/beta/beta4-first-phase-manifest.json`, SHA-256 do arquivo `6e820ce44d6d23141d6cdc57e323e9a42e23c36e14b9741f030952d3772ffb42`. Manifesto de staging Beta 5: `docs/beta/beta5-first-phase-manifest.json`, SHA-256 do arquivo `4e1145798574bce58a72afdbe3150977d3025225b04f962aa46be811eb7077db`. O payload curricular do manifesto Beta 5 tem SHA-256 `dce89cbc9beb1040a5cb993494026ac07a5c0d8d80e19479349e088f225eb6e4`.

O manifesto Beta 4 declara 221 artefatos de origem, 10 unidades e 3 módulos. A conversão da execução Beta 7.1 voltou a validar os hashes de cada unidade, contagens agregadas e IDs antes de persistir. Nenhum Markdown original foi editado ou incluído como cópia curricular nesta branch.

## Inventário verificado

| Unidade | Hash da fonte | Tópicos | Segmentos | Questões | Exercícios | Navegador |
|---|---|---:|---:|---:|---:|---|
| 1.1 — Computação e software | `a1177bdc030db528d67bad76f8ee4c7670e616bf45b7780a9087c1283d7adc3c` | 5 | 8 | 5 | 3 | BROWSER_VERIFIED |
| 1.2 — Ambiente de desenvolvimento | `e7aa639a0b2184082848dfea3d08d1d57d9499da59d1841a1cb2c13775a4e24e` | 5 | 5 | 5 | 3 | BROWSER_VERIFIED |
| 2.1 — Terminal e navegação | `41df0119619e2f7ba44ffbfebb27edc310ac7f5c930cb036614084bacc527319` | 4 | 4 | 5 | 3 | BROWSER_VERIFIED |
| 2.2 — Sistema e operação | `443cd3f2cafd2e85e6528afb19cf1ee51ef109cdbae004776091d66e8f8b4575` | 3 | 3 | 5 | 3 | BROWSER_VERIFIED |
| 2.3 — Acesso remoto | `4c31d3600578f0bb5b4a98b254fc989ac5a77f3fd78bb2d4b9727d06f44f41bb` | 3 | 3 | 5 | 3 | BROWSER_VERIFIED |
| 3.1 — Git local | `1ec59acae663cc26520e903d43b49efb7cd6ce414189b2543ef1eb9891259691` | 2 | 5 | 5 | 3 | BROWSER_VERIFIED |
| 3.2 — Trabalho com histórico | `a71894ea9ab502f467842a7ba24b08b7fff44e947f5a93793da3498ca32ef146` | 2 | 3 | 5 | 3 | BROWSER_VERIFIED |
| 3.3 — GitHub | `bf7a454d0b2e2c1514dc02f527e45458df5bcb24c241c0b8344a33ec080dbabf` | 4 | 4 | 5 | 3 | BROWSER_VERIFIED |
| 3.4 — Revisita contínua | `6853cb1ca262cdc3276c7cbc7df505292cc4cf7cd3737b3e2cc38220556721b7` | 1 | 3 | 4 | 2 | BROWSER_VERIFIED |
| 3.5 — Projeto incremental da fase | `f2b7ab9454591d5ed02a1e5e70b5331e21aaf36efa5490c147ca693d6d20b877` | 1 | 4 | 0 | 0 | BROWSER_VERIFIED |
| **Total** | — | **30** | **42** | **44** | **26** | **10/10 unidades visitadas** |

Totais adicionais validados estruturalmente: 39 referências, 30 relações e 11 artefatos do projeto 3.5. O conversor produziu 161 blocos no payload aceito pelo importador. Os 30 tópicos e 42 segmentos mantêm associação e ordem; a interface renderiza os tópicos e segmentos recebidos, sem resumir o conteúdo.

## Cobertura por camada

| Verificação | Estado | Evidência |
|---|---|---|
| Conversão, hash e inventário das dez unidades | STRUCTURALLY_VERIFIED | Validador de lote do harness antes de qualquer gravação curricular |
| Importação pelo serviço real | PERSISTENCE_VERIFIED | `run_import` no MongoDB descartável, track draft/private |
| Leitura pelo serviço operacional de trilhas | HTTP_VERIFIED (negação) | 404 para o aluno na trilha privada; publicação continua ausente |
| Prévia HTTP autenticada | HTTP_VERIFIED | três módulos, dez unidades, atividades 1.1, projeto 3.5 e negativas de escopo |
| Browser real | BROWSER_VERIFIED | Playwright/Chromium abriu e conferiu as dez unidades na ordem curricular |
| Quiz funcional por HTTP/browser | PARTIAL | questões estruturais todas; tentativa exercitada nas unidades 1.1 e 2.1 |
| Exercícios | PARTIAL | 26 representados; submissão/feedback exercitados em 1.1; entrega de projeto em 3.5 |
| Conclusão pedagógica da fase | BLOCKED | critérios ambíguos e rubrica do projeto aguardam decisão pedagógica |

O Playwright percorreu 1.1, 1.2, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4 e 3.5 pela navegação da interface. Respondeu quiz em 1.1 e 2.1, enviou exercício em 1.1 e entregou/corrigiu o projeto. Após logout, novo login e recarga, feedback e progresso permaneceram.

## Limite de conclusão

Todas as dez unidades ficam acessíveis na prévia e possuem progresso calculado sem inventar aprovação. A fase declara `BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA`, domínio `NOT_ASSESSED`. Isso é o comportamento intencional enquanto regras de aprovação e critérios do projeto não forem aprovados. Uma jornada funcional de estudo não equivale a conclusão ou domínio pedagógico.
