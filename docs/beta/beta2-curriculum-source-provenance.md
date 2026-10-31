# Beta 2 — proveniência da fonte curricular

## Fontes encontradas

| Fonte | Estado local observado | Conteúdo e integridade | Uso nesta fase |
|---|---|---|---|
| Bundle C16 em `e801cee` | Commitado | 10 fases, 194 nós hierárquicos, 1.691 blocos; os blocos estão em `draft` e são principalmente `theory_text`, `summary` e `instructor_note` | Referência do contrato legado, não fonte pedagógica mais completa |
| `Conteudos/Fase_1/1.1_Computacao_e_software.md` | Rastreado e limpo em `migracao-estrutura@147dc68`; estado curricular `rascunho` | Unidade integral em Markdown, com objetivo, teoria, resumo, 5 questões com gabarito, 3 práticas, critério de conclusão, conexões e 2 referências | Cópia independente usada como fixture da conversão |
| `Conteudos_migrado/Fase_1/` | 221 arquivos Markdown rastreados na Fase 1; sem alterações locais detectadas na árvore consultada | 10 unidades; separa índice, teoria, quiz, gabarito, práticas, soluções, rubrica, conclusão e referências | Fonte segmentada mais estruturada; não foi copiada integralmente |
| `trilha-code-bulk-import.json` e contratos tipados na worktree migratória | Bundle modificado; `backend/curriculum_contract/` e contratos de `docs/migracao/` não rastreados | Validação local somente leitura passou: schema `trilhacode.import_bundle/1.0`, 10 fases, 572 nós, 3.431 blocos, 15 projetos, 55 relações, 1.001 placements; 0 erros bloqueantes, 66 warnings, 214 pendências editoriais e 11 arquivos estruturais fora dos destinos mapeados | Evidência de capacidade do contrato local dirty; não é artefato aprovado ou integrado |

Os números de 572 nós e 3.431 blocos pertencem ao bundle modificado da worktree `migracao-estrutura`; não substituem os números do bundle commitado. O relatório de integridade desse artefato registra 2.890 arquivos migrados, 2.889 registros de mapeamento e uma estrutura não representada (`Fase_2/Projeto_incremental.md`). A validação do bundle é estrutural e não representa aprovação pedagógica humana.

## Unidade piloto e cadeia de origem

- Identidade: `1.1 — Computação e software` (`frontmatter.key=1.1`).
- Caminho de origem: `docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md`.
- Revisão observada: `migracao-estrutura@147dc68`, arquivo rastreado e sem alteração local.
- SHA-256 dos bytes da fonte: `db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4`.
- SHA-256 com CRLF normalizado para LF: `21736a209b840406169d88862f793e848952a402a01a37ae22d974d7bd59e513`.
- Fixture independente: `backend/integration_tests/fixtures/beta2/unit_1_1_computacao_e_software.source.md`, cópia byte a byte; hash verificado contra a fonte.
- Estado de publicação pedagógica: `rascunho`. A prova cria também trilha, nó e blocos em `draft`; não aprova nem publica a unidade.

O índice segmentado declara cinco tópicos e organiza exercícios e gabaritos em arquivos separados. O contrato local tipado associa a unidade `f1-1-1-readme` a cinco tópicos e, contando placements compartilhados, 28 blocos únicos: 5 teorias, 5 quizzes, 5 gabaritos, 3 práticas, 2 soluções, 1 rubrica, 1 checklist, 1 feedback, objetivo, resumo, conclusão e 2 referências. Os 20 placements dessa unidade ainda têm `progress_scope=undecided`. Esses dados são da worktree de migração e não foram copiados para a fixture.

## Decisão de fonte

Para a prova executável, a fonte é **PROPOSED_SOURCE**, não `APPROVED_SOURCE`: a cópia monolítica é limpa, completa e permite demonstrar parsing determinístico sem tocar em arquivos de terceiros. A fonte segmentada e os contratos tipados são estruturalmente mais ricos para uma conversão de fase, mas dependem de revisão e consolidação explícita do trabalho dirty da migração.

Não foi alterado nenhum arquivo curricular ou relatório histórico.
