# Beta 4 — fidelidade do conteúdo

## Resultado de lote

O conversor tipado processou as dez unidades e não marcou nenhuma como `CONVERSION_BLOCKED`. Todas resultaram em `CONVERSION_SUCCESS_WITH_WARNINGS`, pois critérios, respostas de correção, parte das referências/conexões e projeto não têm destino operacional seguro comprovado. Não houve reescrita generativa nem edição da fonte.

| Unidade | Tópicos preservados | Segmentos ordenados | Questões | Exercícios | Artefatos de projeto mantidos fora do payload |
|---|---:|---:|---:|---:|---:|
| 1.1 | 5 | 8 | 5 | 3 | 0 |
| 1.2 | 5 | 5 | 5 | 3 | 0 |
| 2.1 | 4 | 4 | 5 | 3 | 0 |
| 2.2 | 3 | 3 | 5 | 3 | 0 |
| 2.3 | 3 | 3 | 5 | 3 | 0 |
| 3.1 | 2 | 5 | 5 | 3 | 0 |
| 3.2 | 2 | 3 | 5 | 3 | 0 |
| 3.3 | 4 | 4 | 5 | 3 | 0 |
| 3.4 | 1 | 3 | 4 | 2 | 0 |
| 3.5 | 1 | 4 | 0 | 0 | 11 |

Para cada tópico, os segmentos preservam heading, corpo Markdown completo, ordem, caminho e hash. A estrutura importável é hierárquica: Fase → módulo derivado do ID → unidade → tópico → segmentos. O teste compara texto e ordem com artefatos reais de origem, não somente o payload consigo mesmo.

## Estruturas heterogêneas encontradas

O lote inclui quizzes segmentados (há unidades com mais arquivos de quiz do que questões), avaliações integradoras sem vínculo a tópico, a unidade 3.4 com quatro questões e duas práticas e a unidade 3.5 como projeto com brief, quatro marcos, rubrica e checklists, sem quiz ou exercícios convencionais. Os materiais do projeto 3.5 ficam na representação intermediária e não viram blocos de aluno por falta de contrato operacional.

Variações de quiz são aceitas por dois formatos detectados na fonte. Respostas e explicações são extraídas do gabarito correspondente somente quando IDs/cardinalidade coincidem. Itens sem resposta correspondente bloqueiam parsing; o conversor não inventa gabaritos.

## Relações e referências

Foram extraídas 39 referências e 30 declarações de relação. Títulos, URLs e ordem entram no modelo intermediário; a descrição de referência não cabe no schema `reference` atual. Vinte e uma relações entre unidades presentes na fase entram na coleção de relações com `enforced=false`; nenhuma menção contextual foi convertida em pré-requisito obrigatório. Alvos fora da fase ficam no contrato intermediário; duas linhas livres de 3.5 permanecem não resolvidas.

## Perdas evitadas e pendências

O lote não condensa tópicos, não descarta exemplos nem sobrescreve respostas. O payload deliberadamente não inclui conclusão, rubricas/respostas de exercícios, checklists, descrições de referências, projeto por marcos e relações sem alvo interno. Esses elementos aparecem como `REQUIRES_ADAPTER`, não como ausência pedagógica. A lista por unidade está no manifesto agregado.
