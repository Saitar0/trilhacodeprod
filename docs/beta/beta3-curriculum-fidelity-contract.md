# Beta 3 — contrato de fidelidade curricular

## Escopo e proveniência

Esta especificação é uma prova isolada da unidade `1.1 — Computação e software`. A origem é a cópia Beta 2 em `backend/integration_tests/fixtures/beta2/unit_1_1_computacao_e_software.source.md`, vinculada ao caminho curricular registrado no manifesto. O SHA-256 bruto esperado é `db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4`; a conversão falha se o hash divergir. A fonte permanece classificada `rascunho` e `APPROVED_FOR_ISOLATED_EXPERIMENT`; isso não aprova publicação nem importação operacional.

O original e a worktree de migração foram somente lidos. O conversor compõe o parser Beta 2 existente e não reescreve o Markdown. A comprovação da preservação teórica compara a concatenação dos segmentos fonte com a teoria parseada, byte textual após decodificação UTF-8.

## Contrato intermediário

`backend/curriculum_contract/experimental_beta_curriculum_fidelity.py` define modelos Pydantic estritos (`extra="forbid"`, imutáveis e com entradas ocultadas em erros). O modelo contém identidade e versão da origem, hash bruto e normalizado, objetivos, metadados, grupos e segmentos de teoria, resumo, questões, alternativas e resposta restrita, exercícios e campos de corretor, critério de conclusão, relações, referências, seções sem destino e disposições de mapeamento.

IDs derivam da chave de origem, títulos e posições existentes; nenhuma geração aleatória é usada. A conversão verifica duplicidades, ordem contínua, referências a tópicos, gabarito pertencente às alternativas, formato de tags e número de minutos. Seções ou subtítulos não reconhecidos falham ou ficam explicitamente listados como sem destino; não são silenciosamente descartados.

## Fidelidade observada na unidade

| Elemento | Preservação experimental |
|---|---|
| Tópicos da estrutura migratória | 5 grupos ordenados, conforme o contrato de origem observado |
| Seções H3 da teoria | 8 segmentos individuais, texto Markdown integral, heading e ordem preservados |
| Objetivo e resumo | Texto preservado; objetivo mapeado à descrição do nó e resumo a bloco próprio |
| Quiz | 5 questões, alternativas, IDs estáveis, gabaritos e explicações no contrato restrito |
| Prática | 3 exercícios de correção manual, enunciado e ordem preservados; soluções/critérios classificados como restritos |
| Conclusão | Formulação textual preservada; regra automática permanece nula |
| Conexões | 3 relações textuais preservadas, sem resolver links para IDs nem impor pré-requisito |
| Referências | 2 títulos, URLs, descrições e Markdown original preservados no contrato intermediário |
| Proveniência | Caminho, revisão, hash, versão do parser e do adaptador no manifesto |

## Projeção de importação

O payload experimental usa o envelope real `track/options/nodes/relations`, com uma trilha privada e em `draft`, um nó `submodule` e 19 blocos ordenados: 8 `theory_text`, 1 `summary`, 5 `quiz`, 3 `exercise_open` e 2 `reference`. Tags, duração e classificações do frontmatter também são preservadas nos campos admitidos do nó.

Os cinco grupos são codificados nos IDs de referência estáveis dos segmentos, mas o schema persistido não possui uma propriedade de agrupamento de tópico. Assim, os blocos permanecem ordenados e rastreáveis, enquanto a navegação agrupada exige adaptador futuro. O payload não contém respostas de exercícios, rubricas, critérios de conclusão, relações não resolvidas nem descrições de referências sem destino.

Os gabaritos de quiz são campos restritos do bloco versionado no ambiente de teste em rascunho. A regra de publicação e o endpoint do aluno não foram exercitados; qualquer publicação depende de ACL, projeções e política de resposta aprovadas. Não usar `model_dump()` do contrato intermediário como resposta pública: usar somente as projeções explícitas e um autorizador futuro.

## Limites

Esta prova não aprova pedagogicamente a origem, não transforma uma unidade em conteúdo publicado, não testa a interface nem a jornada E2E e não atesta o runtime. Metadados genéricos de editor podem guardar campos de quiz que não são editáveis por ele. Soluções, conclusão estruturada, relações resolvidas e descrições de referência continuam sem destino operacional demonstrado.
