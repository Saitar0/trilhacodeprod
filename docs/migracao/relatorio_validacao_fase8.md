# Validação da migração estrutural — Fase 8

**Base:** `b74e053879bd7c8ec8093479e5c645bba9cc6be8` · **branch:** `migracao-estrutura` · **resultado técnico:** PASSOU COM RESSALVAS.

## Contagens

| Unidade | Arquivos |
|---|---:|
| 37.1 | 8 |
| 37.2 | 8 |
| 37.3 | 14 |
| 38.1 | 22 |
| 38.2 | 21 |
| 39.1 | 22 |
| 39.2 | 13 |
| 39.3 | 16 |
| **Total** | **124** |

| Tipo de arquivo | Quantidade |
|---|---:|
| `answer_key` | 15 |
| `checklist` | 6 |
| `conexoes` | 8 |
| `criterio` | 8 |
| `flashcards` | 5 |
| `objetivo` | 8 |
| `practice` | 11 |
| `project_milestone` | 4 |
| `project_scenarios` | 1 |
| `project_scope` | 2 |
| `quiz` | 15 |
| `referencias` | 8 |
| `resumo` | 6 |
| `rubric` | 2 |
| `theory` | 17 |
| `topic_index` | 8 |

## Integridade e cobertura

- Fontes ativas: 8/8; assuntos convencionais: 13; contêineres de projeto: 2.
- Blocos de teoria: 21 (19 microtópicos titulados e duas seções sintéticas); questões: 15; respostas inline separadas: 15; práticas: 11; flashcards: 9.
- Arquivos gerados: 124; IDs únicos na árvore e sem colisão com os 2161 IDs anteriores.
- Registros de origem→destino: 192; a auditoria por intervalos confirmou que cada trecho não estrutural possui destino e não há sobreposição.
- Cabeçalhos de contêiner sem arquivo próprio (somente estrutura):

| Cabeçalho | Ocorrências |
|---|---:|
| `## Atividades` | 4 |
| `## Entregas verificáveis` | 1 |
| `## Flashcards` | 3 |
| `## Quiz` | 3 |
| `## Teoria` | 5 |

- Metadados originais, incluindo `key`, comparados com as oito fontes e preservados nos READMEs.
- Os 15 pares Q/gabarito foram reconstruídos literalmente; o limite de separação foi conferido como `? **` em cada item. A concatenação Q+K reproduz cada bloco original.
- Os itens compartilhados têm um único arquivo em `90_integracao/` e associações coerentes no frontmatter/cobertura.
- 39.2: quatro microtópicos, checklist de 11 itens, rubrica de seis dimensões/0–2 e cinco verificações por cenário preservados.
- 39.3: quatro entregas, quatro aceites, checklist de 12 itens e rubrica de seis dimensões/0–2 preservados. T1–T5 permanece exclusivamente no arquivo da Entrega 3.
- Frontmatter YAML válido em todos os arquivos; paths e `arquivo_id` únicos.
- Links Markdown relativos resolvidos: 120; wikilinks preservados sem reescrita: 0.

## Normalizações estruturais autorizadas

- 39.2: `../../Guia_de_Projetos_e_Rotacao_de_Tipos.md` → `../../../Guia_Projetos_e_Rotacao_de_Tipos.md`; 1 ocorrência(s); alvo verificado `docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md`.
- 39.2: `../../Guia_Projetos_e_Rotacao_de_Tipos.md` → `../../../Guia_Projetos_e_Rotacao_de_Tipos.md`; 1 ocorrência(s); alvo verificado `docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md`.
- 39.3: `../../Guia_Projetos_e_Rotacao_de_Tipos.md` → `../../../Guia_Projetos_e_Rotacao_de_Tipos.md`; 2 ocorrência(s); alvo verificado `docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md`.

Os textos visíveis dos links foram preservados. Uma referência de 39.2 usava um nome de arquivo que não existe; foi apontada para o único guia existente com o mesmo título visível. A raiz do vault Obsidian continua não confirmada.

## Escopo preservado

- Fases 1–7: 2161 arquivos, hashes idênticos ao pré-voo.
- Conteúdos originais e backups: 133 arquivos, hashes idênticos ao pré-voo.
- JSON de importação, páginas da fase e guia de projetos: hashes idênticos ao pré-voo.
- Cópias auxiliares 37.1/37.2 em `Conteudos/Fase_7/`: intactas, fora da árvore Fase 8 e não declaradas aposentadas.
- Nenhum importador executado; nenhum commit criado.
