# Relatório de validação — Fase 2

- Commit-base: `7028682ab46dd6186c274f9655bd7dce3c2e3612`
- Branch: `migracao-estrutura`
- Destino: `docs/courses/trilhacode/Conteudos_migrado/Fase_2/`
- Unidades: 7
- Assuntos: 17
- Microtópicos de teoria: 30
- Questões: 35
- Práticas: 21
- Arquivos de curso gerados: 144
- Mapeamentos físicos e remoções aprovadas: 209

## Contagem por tipo

- `answer_key`: 18
- `answer_key_pratica`: 8
- `checklist`: 12
- `conexoes`: 7
- `criterio`: 7
- `objetivo`: 7
- `practice`: 21
- `project_index`: 1
- `quiz`: 18
- `referencias`: 7
- `resumo`: 7
- `rubric`: 7
- `theory`: 17
- `topic_index`: 7

## Contagem por unidade

| Unidade | Arquivos | Blocos mapeados | Resultado |
|---|---:|---:|---|
| 4.1 | 21 | 28 | OK |
| 4.2 | 18 | 28 | OK |
| 4.3 | 22 | 30 | OK |
| 5.1 | 23 | 34 | OK |
| 5.2 | 21 | 29 | OK |
| 5.3 | 19 | 31 | OK |
| 5.4 | 19 | 29 | OK |

## Validações textuais e estruturais

- Cada arquivo de conteúdo é exatamente a concatenação dos fragmentos registrados no mapeamento, com somente CRLF/CR normalizado para LF; cada fragmento foi localizado na fonte, salvo as duas relações duplicadas explicitamente removidas.
- Os 30 títulos de teoria correspondem aos destinos do manifesto; os 35 enunciados e gabaritos e as 21 práticas foram verificados por ID e conteúdo.
- Blocos de código comparados por conteúdo integral; respostas, soluções, checklists, critérios e rubricas mapeados em arquivos próprios quando existem.
- O bloco misto 5.1/P2 foi separado pelos segmentos literais do manifesto; segmentos têm correspondência exata com a fonte e foram direcionados sem sobreposição.
- Metadados originais preservados no frontmatter do README; frontmatter dos filhos parseado e IDs únicos, sem colisão com os 221 IDs da Fase 1.
- Links Markdown relativos dos READMEs e sete links do índice do projeto resolvem para arquivos existentes.
- Originais Fase 2, notas gerais da fase, referências e JSON possuem SHA-256 idêntico ao pré-voo.
- Os 221 arquivos migrados da Fase 1 mantêm seus hashes pré-geração.
- JSON não foi alterado; importador não foi executado; nenhum commit foi criado.

## Limitações

- Wikilinks Obsidian para documentos externos à árvore migrada dependem da raiz do vault e da integração final; mantidos conforme decisão aprovada.
- A existência de textos de conexão repetidos foi tratada somente nos dois casos autorizados no manifesto.
