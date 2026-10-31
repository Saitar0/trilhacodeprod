# Beta 3 — mapeamento de conteúdo tipado

Fonte: unidade 1.1, fixture independente com o hash confirmado na Beta 2. Estados descrevem somente o adaptador experimental e o schema versionado no código, não disponibilidade para alunos.

| Origem | Contrato intermediário | Destino C16 / leitura | Estado | Perda ou ação |
|---|---|---|---|---|
| `frontmatter.key`, título e estado | Proveniência e identidade da unidade | `nodes.title`, `meta.import_ref`; destino sempre draft | `SUPPORTED_WITH_TRANSFORMATION` | Revisão/hash ficam no manifesto, não no documento importado |
| tipo, caráter, profundidade | Campos tipados do nó | `nodes.pedagogical_type`, `requirement`, `depth` | `SUPPORTED_EXACT` | Taxonomia precisa existir; exercitada com cópia sintética |
| tags e duração | `tags`, `estimated_minutes` | Campos tipados do nó; tags resolvidas pelo importador | `SUPPORTED_EXACT` | Tag ausente pode ser criada no banco descartável |
| objetivo | Texto original | `nodes.description` | `SUPPORTED_EXACT` | Não há bloco `objective` dedicado |
| 5 grupos / 8 seções H3 | `TheoryTopic` e `TheorySegment` | 8 `theory_text` ordenados no nó | `SUPPORTED_WITH_TRANSFORMATION` | Agrupamento está no ref/manifesto, não como entidade de navegação |
| resumo | Texto original | bloco `summary.data.body` | `SUPPORTED_EXACT` | — |
| quiz: pergunta e alternativas | `QuizQuestion`, `QuizOption` | bloco `quiz` versão 1 | `SUPPORTED_WITH_TRANSFORMATION` | Uma pergunta por bloco; metadata genérica de editor é legada |
| quiz: resposta e explicação | projeção restrita do modelo | `correct_option_id`, `feedback` no bloco draft | `SUPPORTED_WITH_TRANSFORMATION` | Uma explicação fonte preenche `feedback.correct` e `feedback.incorrect`; confirmar a semântica antes da publicação |
| exercício: enunciado e instruções | `ManualExercise.student_prompt` | `exercise_open.data.prompt`, `grading=manual` | `SUPPORTED_EXACT` | Não executar código nem auto corrigir |
| resposta e critérios do corretor | campos restritos do contrato | Nenhum destino seguro comprovado | `REQUIRES_ADAPTER` | Não persistidos; schema/leitor comum não provam ACL |
| critério de conclusão | texto literal + sem regra automática | Nenhum campo semântico comprovado | `REQUIRES_ADAPTER` | Não converter para percentual ou domínio |
| conexões | relação literal, caminho e âncora | `relations` C16 exige refs resolvidos | `REQUIRES_ADAPTER` | Links ainda não resolvidos para IDs de nó |
| referência: título e URL | referência com ordem e Markdown fonte | `reference.data.citation/url` | `SUPPORTED_WITH_TRANSFORMATION` | — |
| descrição de referência | descrição preservada | Nenhum campo do bloco `reference` | `REQUIRES_ADAPTER` | Não truncada para caber em `citation` |
| ordem e identidade | refs estáveis e posição da fonte | `nodes.order`, `content_blocks.order`, `meta.import_ref` | `SUPPORTED_WITH_TRANSFORMATION` | Ordem de bloco persistida; serviço de leitura staff confirmou sequência |
| seção desconhecida | seção integral no modelo e hash no manifesto | Sem destino | `REQUIRES_ADAPTER` | Não importada; nome/hash/contagem visíveis no manifesto |

O nó-piloto totaliza 19 blocos. `validate_import_shape` do backend aceitou o envelope experimental; o `run_import` real também persistiu os blocos. O schema de `block_types` permite campos legados, mas emite avisos para campos versionados de quiz que não são declarados pela metadata genérica. O validador versionado `normalize_quiz` aceita o formato restrito.

Não existe perda silenciosa na saída: cada lacuna tem disposição explícita. A conversão de fase completa exige validar refs, árvore fase→módulo→unidade→tópico, placements compartilhados e os campos sem destino antes de gerar payload.
