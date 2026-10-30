# Auditoria global das Fases 1–10

**Data:** 2026-10-27  
**Branch:** `migracao-estrutura`  
**HEAD:** `147dc68b81169f66b0ba3802fa2f26e5130923a3`  
**Veredito:** **APROVADA COM RESSALVAS — integridade estrutural e documental; ainda não pronta para importação.**

## Escopo e método

Auditoria somente de leitura das dez árvores em `docs/courses/trilhacode/Conteudos_migrado/`, dos dez manifestos e relatórios de mapeamento, das fontes sob `docs/courses/trilhacode/Conteudos/`, do JSON atual e dos artefatos de projeto. Foram verificadas contagens, destinos, frontmatters e IDs, referências locais, links Markdown, hashes e seletores de origem disponíveis nos mapas. Nenhum importador foi executado e o JSON não foi alterado.

Para as Fases 1–5, a evidência textual usada é a reconstrução e auditoria final homologada de cada fase. A nova conferência global verificou suas árvores, manifestos, origens/destinos e relatórios. Para as Fases 6–7, offsets e hashes registrados nos mapas foram conferidos diretamente; para as Fases 8–10, os segmentos `texto_origem` foram comparados diretamente às fontes. Os resultados de cada reconstrução isolada homologada também foram considerados. Portanto, esta auditoria não substitui as evidências detalhadas por bloco nos relatórios de fase.

## Inventário reconciliado

| Fase | Unidades | Projetos | Assuntos convencionais | Microtópicos | Questões | Práticas | Flashcards | Arquivos | Mapeamentos |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 10 | 1 | 29 | 42 | 44 | 26 | 0 | 221 | 272 |
| 2 | 7 | 0 | 17 | 30 | 35 | 21 | 0 | 144 | 209 |
| 3 | 14 | 2 | 40 | 53 | 59 | 36 | 0 | 313 | 581 |
| 4 | 17 | 2 | 49 | 68 | 65 | 43 | 3 | 395 | 635 |
| 5 | 20 | 2 | 59 | 81 | 90 | 54 | 0 | 483 | 762 |
| 6 | 20 | 2 | 57 | 74 | 80 | 52 | 6 | 449 | 616 |
| 7 | 7 | 0 | 23 | 28 | 35 | 21 | 0 | 156 | 210 |
| 8 | 8 | 2 | 13 | 19 | 15 | 11 | 9 | 124 | 192 |
| 9 | 16 | 2 | 47 | 47 | 25 | 33 | 27 | 301 | 428 |
| 10 | 12 | 2 | 40 | 40 | 50 | 30 | 0 | 304 | 406 |
| **Total** | **131** | **15** | **374** | **482** | **498** | **327** | **45** | **2.890** | **4.311** |

Os projetos estão incluídos nas 131 unidades, mas não na soma dos 374 assuntos convencionais. A unidade 8.4 não aparece em manifesto nem na árvore da Fase 3. A Fase 2 mantém `Projeto_incremental.md` como índice em nível de fase, fora das 131 linhas de unidade do inventário.

### Arquivos físicos por tipo

| Tipo de arquivo | Total |
|---|---:|
| `objetivo` | 131 |
| `topic_index` (README de unidade) | 131 |
| `resumo` | 123 |
| `criterio` | 130 |
| `conexoes` | 131 |
| `referencias` | 131 |
| `theory` | 379 |
| `quiz` | 398 |
| `answer_key` | 398 |
| `practice` | 327 |
| `answer_key_pratica` (solução/feedback) | 212 |
| `flashcards` | 30 |
| `flashcard` | 6 |
| `rubric` | 178 |
| `checklist` | 89 |
| `acceptance_criteria` | 17 |
| `milestone` | 36 |
| `project_milestone` | 20 |
| Outros tipos estruturais/de projeto | 23 |
| **Total** | **2.890** |

Os 498 itens de questão e os 45 flashcards são contagens de conteúdo, não contagens de arquivos: há itens agrupados no mesmo arquivo. Os 398 arquivos de quiz e 398 arquivos de gabarito não significam que haja somente 398 questões. De modo semelhante, os 327 enunciados de prática coexistem com 212 arquivos de solução/feedback, pois nem toda prática tem solução própria e alguns arquivos agrupam conteúdo.

## Mapeamentos e cobertura das fontes

- Os dez CSVs contêm **4.311 registros**. Eles apontam para **2.879 destinos físicos únicos** existentes. Dez README estruturais da Fase 1 e o índice `Projeto_incremental.md` da Fase 2 completam os **2.890 arquivos**.
- Na Fase 2, dois registros de remoção de conexões duplicadas estão autorizados; não correspondem a arquivos de destino. Não foram encontrados outros destinos ausentes, origens ausentes ou arquivos migrados sem cobertura, além dos 11 arquivos estruturais acima.
- Foram localizados 133 Markdown sob `Conteudos/`: 131 origens ativas únicas mais as cópias de `37.1` e `37.2` em `Conteudos/Fase_7/`. As cópias da Fase 7 diferem das fontes oficiais da Fase 8, foram preservadas e não foram migradas como unidades ativas da Fase 7.
- Conferência textual direta de **1.852 registros**: Fase 6, **616/616 hashes** de segmentos; Fase 7, **210/210 hashes**; Fase 8, **192/192 segmentos de texto**; Fase 9, **428/428**; Fase 10, **406/406**. Fases 1–5 remetem às auditorias homologadas por fase; a Fase 1 registra 272/272 blocos comparados à extração/hash e as auditorias F2–F5 registram reconstruções sem divergências materiais.
- Os arquivos compartilhados mantêm um único caminho físico conforme o manifesto, com associações a múltiplos assuntos. Os dois casos de remoção estrutural autorizada estão distinguidos de perda de conteúdo.
- Os manifestos declaram **2.486 aliases de arquivo**; todos resolvem para arquivos existentes. Nos esquemas que carregam `arquivo_id` no manifesto, **1.334 IDs** conferem com o frontmatter do destino. Os esquemas mais antigos das Fases 1–2 não registram esse campo no manifesto; seus IDs foram validados diretamente por unicidade e prefixo nos arquivos.

## Frontmatter, IDs e estrutura

Foram percorridos os **2.890 Markdown** das dez árvores. Todos possuem frontmatter YAML parseável, `arquivo_id` presente, prefixo da fase correspondente (`f1-` a `f10-`) e corpo não vazio. Foram encontrados **2.890 IDs únicos**, zero colisões e zero arquivos vazios. O parser de auditoria rejeitou chaves YAML duplicadas; nenhuma foi encontrada. Os caminhos de saída nos mapas são únicos por fase e todos os destinos físicos declarados existem.

O CSV [`INVENTARIO_GLOBAL.csv`](INVENTARIO_GLOBAL.csv) contém uma linha por unidade, com fase, ID, título, módulo, fonte relativa ao repositório, metadados originais, quantidades por conteúdo e arquivos físicos, links e escala registrada. Os nomes dos módulos das Fases 1–3 foram obtidos dos títulos de módulo nas páginas oficiais dessas fases, pois os manifestos antigos não traziam esse campo.

## Links e referências

| Classe verificada | Total | Resultado |
|---|---:|---|
| Links Markdown locais relativos | 2.785 | Todos resolvem para arquivo ou README existente |
| Links Markdown externos | 556 | Sintaxe reconhecida; disponibilidade remota não foi consultada |
| Wikilinks Obsidian | 94 | Preservados; resolução depende da raiz do vault, ainda não confirmada |
| Links ao guia rastreado de projetos | 18 | Destinos existentes e rastreados |
| Links Markdown locais quebrados | 0 | Nenhum encontrado |
| Links Markdown relativos entre fases | 0 | Nenhum detectado |

As referências a `47.2` e `47.3` em 47.1 são menções textuais sem link Markdown e sem destino ativo confirmado. Permanecem como pendência editorial, não como link quebrado. Não foram criadas referências ao guia local de produção não rastreado.

## Projetos, entregas e critérios

Há 15 unidades classificadas como projeto. A escala registrada nas fontes e mapas é:

| Escala | Projetos |
|---|---|
| 0–4 | 3.5, 8.5, 8.6, 24.3, 24.4, 31.4, 31.5 |
| Sem escala numérica | 16.2, 16.3 |
| 0–2 | 39.2, 39.3, 46.2, 46.3, 52.1, 52.2 |

Há 56 arquivos de marco/entrega em projetos com estrutura formal de quatro etapas. A unidade 39.2 é projeto sem marcos formais: seus materiais de apoio, cenários, checklist e rubrica não foram convertidos em marcos. O conjunto contém 89 arquivos `checklist`, 17 arquivos `acceptance_criteria` e 178 arquivos `rubric`; critérios de aceite também podem permanecer associados ao arquivo do marco, por isso a contagem de arquivos não equivale à contagem de critérios.

A revisão da Fase 8 confirma que a tabela T1–T5 de 39.3 está associada à Entrega 2 (`02_fatia_vertical_risco.md`). A Entrega 3 contém cinco itens sobre instrumentação por tipo. A correção documental foi versionada separadamente antes da migração da Fase 9.

## Integridade histórica e Git

- Commit de homologação da Fase 10: `147dc68b81169f66b0ba3802fa2f26e5130923a3`, pai `2f3d8977e7d6c7a74e5f11abc4dec7e66660bc4d`, com **310 caminhos** autorizados.
- O commit da Fase 10 não altera as árvores das Fases 1–9, fontes originais nem JSON. A verificação `git diff` entre a base F10 e HEAD confirma que esses caminhos permanecem iguais. O checkout está sem alterações rastreadas.
- O JSON atual tem SHA-256 `43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7`, 194 nós e 1.691 blocos (`theory_text`: 1.567; `summary`: 123; `instructor_note`: 1). Não foi alterado nem regenerado.
- Não foram encontrados diretórios separados de backup sob `Conteudos/`. Nenhuma afirmação é feita sobre backups que não estavam disponíveis.
- Os oito itens locais não rastreados anteriores foram preservados. Os três relatórios globais desta execução também permanecem não rastreados; nenhum foi staged ou commitado.

## Compatibilidade e prontidão para importação

**Não recomendamos executar a importação ainda.** A migração documental está estruturalmente íntegra, mas o JSON não foi regenerado a partir das árvores e manifestos. A inspeção do código atual mostra que `backend/constants.py` define a hierarquia padrão como `phase → module → submodule → topic`; o modelo atual precisa de um mapeamento explícito entre essa hierarquia e a organização de assuntos/arquivos migrada.

`backend/seed.py` declara tipos como `theory_text`, `summary`, `checklist`, exercícios, `quiz`, `flashcard`, `instructor_note` e referências. `frontend/src/components/blocks/BlockRenderer.tsx` tem renderizadores para esses tipos e envia tipos desconhecidos ao `GenericBlock`. Não há tipo nativo `answer_key` nessa lista. A decisão já aprovada mantém gabaritos em `theory_text` no JSON até uma tarefa separada para estender importador e renderer; essa limitação precisa permanecer explícita. O futuro gerador também precisa mapear IDs globais, relações, conteúdo compartilhado, soluções, rubricas, aceites/checklists e arquivos de projeto de forma determinística.

Nenhum importador foi executado, nenhum JSON definitivo foi produzido e nenhuma modificação curricular foi feita.
