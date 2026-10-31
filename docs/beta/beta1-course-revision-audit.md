# Beta 1 — auditoria da revisão curricular

## Fontes e estado

Contagens foram feitas em leitura. Os estados Git não são intercambiáveis:

| Fonte | Estado | Conteúdo observado | Interpretação |
|---|---|---|---|
| C16 `docs/courses/trilhacode/` | Commitado em `6c227fa6` | 159 Markdown + 1 JSON | Snapshot versionado pela base auditada |
| Bundle C16 | Commitado | 10 fases, 53 módulos, 131 unidades, 194 nós, 1.691 blocos, 50 relações | Legacy import contract; todos os blocos draft |
| Checkout original sujo | Não commitado | 133 Markdown em `Conteudos` (131 ativos + 2 arquivados) e 2.890 Markdown em `Conteudos_migrado` | Cópia segmentada/revisada vista, não canonical sem diff/decisão |
| Worktree `migracao-estrutura` | 12 commits + alterações locais | Conteúdo/mapeamentos e bundle/implementações não commitadas | Não integrado a C16 |

O README do checkout original apresenta 10 fases, 53 módulos, 131 unidades e estimativa de 26.190 minutos (436,5 horas); isso é estimativa editorial, não tempo observado com alunos.

## Snapshot C16 por fase

| Fase | Unidades |
|---:|---:|
| 1 | 10 |
| 2 | 7 |
| 3 | 14 |
| 4 | 17 |
| 5 | 20 |
| 6 | 20 |
| 7 | 9 |
| 8 | 8 |
| 9 | 16 |
| 10 | 12 |
| **Total** | **131** |

C16: 1.567 `theory_text`, 123 `summary`, 1 `instructor_note`; 1.691 blocos `draft`. As refs dos 194 nós são únicas; 50 relações resolvem refs existentes no scan. Há ao menos um H1 nos 159 Markdown. Encontradas quatro ocorrências de link quebrado: três em `31.5_Projeto_de_fase_Trilho_B.md` e uma em `39.2_Projeto_incremental_da_fase.md`, apontando para nome de arquivo com `Guia_de_Projetos...` divergente do alvo existente. Heurística estrutural não avalia qualidade pedagógica.

## Artefato migratório separado

O bundle modificado encontrado na worktree de migração declara 10 fases, 53 módulos, 131 unidades, 572 nós, 3.431 blocos em 18 tipos, 15 projetos, 1.001 placements, 55 relações e 214 pendências editoriais; 66 warnings constam no `integrity`. Há 2.890 arquivos segmentados, 2.889 referências de fonte e um artefato estrutural fora dos destinos mapeados. O JSON estava modificado e a worktree contém mais código não rastreado, por isso estes totais são evidência daquele artefato local, não release.

Um relatório da worktree afirma que a persistência editorial não se conecta à rota/importador/publicação/progresso/quizzes/frontend. Registra decisões pendentes de progress scope compartilhado, publicação, placement, projeto, retenção e outros pontos. É evidência histórica/autorrelatada da worktree, não repetida por esta fase.

## Limites e follow-up

A auditoria não prova leitura de cada arquivo, revisão semântica, correção de todos os exercícios, resolução de autoria/licenças, tempo real, domínio ou importação. Recomenda-se amostrar unidade inicial/intermediária/avançada, quiz com gabarito, exercício de rubrica e projeto, traçando origem→ID→bloco→renderer→tentativa/submissão→conclusão. Nenhuma aula ou conteúdo foi alterado nesta Beta 1.
