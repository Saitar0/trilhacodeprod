# Beta 4 — inventário da primeira fase

## Fonte e método

A conversão leu, sem alterar, `docs/courses/trilhacode/Conteudos_migrado/Fase_1` na worktree `migracao-estrutura`, HEAD `147dc68b81169f66b0ba3802fa2f26e5130923a3`. O filtro Git desse diretório não mostrou modificações e `git ls-files` contou 221 arquivos Markdown rastreados. A worktree contém outras alterações alheias fora desse recorte; elas não foram copiadas nem tocadas. A classificação curricular continua `rascunho`, portanto a fonte está autorizada apenas para experimento isolado.

A referência monolítica da unidade 1.1 teve SHA-256 `db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4`, igual ao hash autorizado na Beta 3. A saída de terminal PowerShell chegou a renderizar acentos como `�`; inspeção dos bytes UTF-8 confirmou que isso era uma limitação de exibição, não corrupção da fonte.

O conversor descobre as unidades pelos diretórios e metadados versionados, ordena seus IDs e rejeita artefatos de tipo desconhecido. A separação em três módulos deriva do primeiro componente numérico do ID da unidade; não representa uma aprovação editorial de estrutura.

## Inventário convertido

| Unidade | Módulo | Tópicos | Segmentos teóricos | Arquivos de quiz / questões | Exercícios | Artefatos de projeto | Referências | Relações | Blocos no payload | Estado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1.1 — Computação e software | 1 | 5 | 8 | 5 / 5 | 3 | 0 | 2 | 3 | 19 | Avisos |
| 1.2 — Ambiente de desenvolvimento | 1 | 5 | 5 | 4 / 5 | 3 | 0 | 3 | 3 | 17 | Avisos |
| 2.1 — Terminal e navegação | 2 | 4 | 4 | 3 / 5 | 3 | 0 | 4 | 2 | 17 | Avisos |
| 2.2 — Sistema e operação | 2 | 3 | 3 | 4 / 5 | 3 | 0 | 4 | 4 | 16 | Avisos |
| 2.3 — Acesso remoto | 2 | 3 | 3 | 3 / 5 | 3 | 0 | 3 | 5 | 15 | Avisos |
| 3.1 — Git local | 3 | 2 | 5 | 2 / 5 | 3 | 0 | 5 | 2 | 19 | Avisos |
| 3.2 — Trabalho com histórico | 3 | 2 | 3 | 3 / 5 | 3 | 0 | 6 | 2 | 18 | Avisos |
| 3.3 — GitHub | 3 | 4 | 4 | 5 / 5 | 3 | 0 | 7 | 4 | 20 | Avisos |
| 3.4 — Revisita contínua | 3 | 1 | 3 | 1 / 4 | 2 | 0 | 2 | 2 | 12 | Avisos |
| 3.5 — Projeto incremental da fase | 3 | 1 | 4 | 0 / 0 | 0 | 11 | 3 | 3 | 8 | Avisos; projeto requer adaptador |
| **Total** | **3** | **30** | **42** | **30 / 44** | **26** | **11** | **39** | **30** | **161** | **Nenhuma bloqueada pelo parser** |

O pacote tem 221 arquivos: índices/README, objetivos, teoria, resumos, quizzes, gabaritos, exercícios, rubricas/checklists, critérios, conexões, referências e materiais do projeto. As 30 relações extraídas incluem alvos fora da fase; somente 21 relações com destino interno foram projetadas para importação, todas não obrigatórias (`enforced=false`). Duas linhas de conexão do projeto 3.5 permanecem textuais e não resolvidas. O total de 44 nós persistidos é composto por raiz de fase, três módulos, dez unidades e trinta nós de tópico.

## Limites do inventário

“Arquivo de quiz” conta um artefato Markdown de autoria e “questão” conta um item estruturado extraído; não é uma avaliação pedagógica nem prova de execução na interface. Os 11 artefatos de projeto são brief, marcos e rubricas/checklists associados, não 11 projetos executáveis. O parser converteu todas as dez unidades para o contrato intermediário, mas todas receberam `CONVERSION_SUCCESS_WITH_WARNINGS`: sucesso de parsing não significa destino operacional completo.

O manifesto por unidade e agregado está em [beta4-first-phase-manifest.json](beta4-first-phase-manifest.json). Ele registra caminhos, hashes, IDs, contagens e perdas/destinos sem incluir corpos de origem ou respostas privadas.
