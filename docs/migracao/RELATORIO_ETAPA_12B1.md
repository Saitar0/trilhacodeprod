# Etapa 12B.1 — correção de fidelidade do contrato e conversor

**Resultado:** concluída em amostras; não integrada à plataforma e não pronta para conversão integral.  
**Base:** `migracao-estrutura`, `147dc68b81169f66b0ba3802fa2f26e5130923a3`.  
**Versão do contrato intermediário:** `trilhacode.intermediate/1.1`, com leitura compatível de objetos 1.0.

## Escopo e pré-voo

O trabalho ficou restrito ao contrato intermediário, ao conversor, aos testes e a este relatório. Não houve conversão integral, geração ou alteração do JSON legado, importação, acesso ao MongoDB, modificação da plataforma, das fontes ou das árvores migradas, commit ou push. Os artefatos locais não rastreados anteriores foram preservados.

O checkout permaneceu na branch e no HEAD-base esperados, sem alterações rastreadas nem conteúdo staged. Permanecem 2.890 arquivos nas árvores migradas. O JSON legado manteve SHA-256 `43125C5902168DEF6359E514AD80602A1F7579157E1A0BB16F1F2212EE4C18E7`.

## Incompatibilidades encontradas e correções

| Fonte / caso | Limitação anterior | Representação em 1.1 | Verificação |
|---|---|---|---|
| `Conteudos_migrado/Fase_10/47.1_Uso_assistido/90_integracao/R00_rubrica_praticas.md`, `itens_origem: [P01, P02, P03]` | `RubricBlock` 1.0 permitia um único alvo; a conversão parava com `RUBRIC_TARGET_AMBIGUOUS`. | `target_refs` preserva os três destinos, na ordem declarada. `target_ref` continua como alias de compatibilidade para o primeiro destino. `source_item_labels` e `source_markdown` preservam a lista literal e o texto integral da rubrica. | A amostra 47.1 resolveu P01, P02 e P03 para as três práticas correspondentes e serializou o contrato. Alvo ausente, repetido, ambíguo ou não declarado continua bloqueante. |
| Rubricas de projeto, como 39.2/R00 e aliases de projeto registrados no manifesto | Um rótulo de escala como “6 dimensões” não é um alvo de conteúdo. Inferir um alvo por proximidade poderia associar incorretamente a rubrica. | A associação a projeto é aceita somente quando o contexto do manifesto identifica explicitamente a rubrica como de nível de projeto; os rótulos originais continuam preservados. Rubricas comuns exigem alvos identificáveis por fonte. | Casos sem associação segura produzem `RUBRIC_TARGET_MISSING` ou `RUBRIC_TARGET_NOT_FOUND`; não há fallback por proximidade. |
| Arquivos `criterio` da unidade | 11 ocorrências eram convertidas para `ConclusionBlock`, confundindo critério de conclusão com resumo/conclusão. | Novo `CompletionCriteriaBlock` guarda o corpo literal, rótulos de origem, ordem, associação curricular e somente relações explicitamente documentadas. | Teste compara o corpo convertido com o corpo da fonte. Nenhuma regra de aprovação é inferida. |
| `project_decisions`, `project_scenarios` e `project_review` | Decisões e cenários eram aproximados como checklists. | Tipos distintos `ProjectDecisionBlock`, `ProjectScenarioBlock` e `ProjectReviewBlock` preservam corpo Markdown literal, rótulos de origem, ordem e relações explícitas. | Testes reais verificam tipo e corpo integral, sem transformar decisão em escolha obrigatória de produto. |
| Corpos de entregas e marcos | 20 textos de etapas eram copiados para blocos `PracticeBlock` apenas porque o modelo não tinha campo de corpo na etapa. | `ProjectDelivery.body` e `ProjectMilestone.body` preservam título e Markdown da entrega/marco diretamente na entidade correspondente. | Fixture verifica Markdown, código cercado e ausência de uma prática sintética para a mesma origem. |
| Aceites, checklists e rubricas | A projeção tipada podia perder texto introdutório, marcadores de checkbox, rótulos ou disposição literal. | Aceites mantêm `body`, itens projetados, `source_item_labels` e relações explícitas; checklists mantêm `source_markdown` e estado marcado/não marcado; rubricas mantêm `source_markdown` junto às dimensões tipadas. | Testes comparam o texto bruto e verificam estados de checkbox. |
| Gabaritos e flashcards | Campos tipados de resposta/frente/verso não guardavam o segmento Markdown original. | `AnswerKeyBlock.source_markdown` mantém cada segmento de resposta; `FlashcardBlock.source_markdown` mantém o corpo Markdown de origem, além dos campos tipados e feedback separado quando presente. | Testes reconstroem os arquivos de gabarito pela concatenação dos segmentos e verificam o vínculo questão–resposta; flashcards mantêm a fonte literal. |

### Rótulos de alvos e limites

Em 47.1, o vínculo é comprovado por três práticas P01–P03 existentes e pela lista explícita no frontmatter da rubrica. Na amostra, `target_refs` resultou em `f10-47-1-p01`, `f10-47-1-p02` e `f10-47-1-p03`, nessa ordem. A rubrica permanece um bloco canônico; não é copiada para cada prática.

Para rubricas de projeto, o manifesto fornece a evidência do alias e do contexto. Se um rótulo não resolver univocamente para uma prática/etapa, se duas entidades corresponderem ao mesmo rótulo ou se a fonte omitir o alvo, a conversão falha com diagnóstico estruturado. A exceção de rubrica de projeto não é aplicada às rubricas multi-alvo de prática.

## Compatibilidade do contrato

O schema foi versionado de `trilhacode.intermediate/1.0` para `trilhacode.intermediate/1.1`. A validação ainda aceita contratos 1.0: campos adicionados permanecem opcionais para esses objetos. Para 1.1, o validador exige os dados de origem necessários à fidelidade e a lista explícita e completa de alvos da rubrica, mantendo `target_ref` alinhado ao primeiro item para consumidores legados do contrato intermediário.

Foram adicionados diagnósticos bloqueantes específicos para lista de alvos ausente, alvo inexistente, referência primária fora de ordem, rótulos duplicados e resolução ambígua. Relações `related_refs` só são aceitas se apontarem para entidades presentes. A proveniência continua contendo caminho de origem e SHA-256; a serialização canônica segue determinística. Nenhum schema de produção foi alterado.

As alterações são compatíveis com o pacote intermediário, não com o importador de produção: não se afirma que a plataforma atual aceite os tipos 1.1. A adaptação do importador e do renderer continua fora desta etapa.

## Reexecução das amostras

As mesmas 12 unidades da Etapa 12B foram reconvertidas em memória a partir dos manifestos e arquivos migrados. Foram processados 332 arquivos de origem, com 572 nós, **223 blocos**, seis projetos e 48 colocações compartilhadas. Todos os contratos válidos serializaram em JSON canônico. A amostra adicional 47.1 processou 38 arquivos de origem, 60 nós e 29 blocos; criou uma rubrica com três alvos ordenados e manteve três pendências editoriais: referências textuais a `47.2` e `47.3` e raiz do vault Obsidian não confirmada.

O relatório da 12B registrava 243 blocos. A diferença de 20 é intencional e rastreável: eram os 20 textos de entrega/marco duplicados como `PracticeBlock`; agora cada texto permanece no campo `body` da entrega ou marco de origem. Não houve remoção do texto nem mudança na quantidade de unidades, fontes mapeadas, nós, projetos ou colocações compartilhadas.

## Tipagem e verificações

Na primeira verificação de mypy que incluía o teste legado da 12A foram identificados oito erros de tipagem localizados no teste: acesso a campos de contrato ainda opcionais sem narrowing e acesso a propriedades de variantes de uma união sem refinamento do tipo. Os testes foram ajustados com asserções de existência e narrowing explícito (`isinstance`). Não houve `Any`, supressão geral nem enfraquecimento das regras do schema; os testes funcionais permanecem ativos.

| Verificação | Resultado |
|---|---|
| Testes do contrato 12A, conversor 12B/12B.1 e regressão `test_import_payload_shape.py` | **81 passaram**. |
| Ruff `check` no pacote e testes relevantes | **Aprovado**. |
| Ruff `format --check` | **Aprovado; 6 arquivos formatados**. |
| Mypy no pacote e testes 12A/12B/12B.1 | **Aprovado; 6 arquivos sem problemas**. |
| `compileall` nos módulos e testes | **Aprovado**. |
| Banco/importador/frontend | Não executados; fora do escopo. |

## Arquivos alterados ou criados

- `backend/curriculum_contract/models.py` — versão 1.1 e tipos/campos fiéis às fontes.
- `backend/curriculum_contract/__init__.py` — exportação dos novos tipos e versão legada.
- `backend/curriculum_contract/converter.py` — resolução explícita de alvos e conversão sem aproximações dos tipos corrigidos.
- `backend/curriculum_contract/validation.py` — validações de alvos, corpos de origem e relações.
- `backend/unit_tests/test_curriculum_contract.py` — compatibilidade, múltiplos alvos e erros de alvo.
- `backend/unit_tests/test_curriculum_markdown_converter.py` — regressões das amostras e testes de fidelidade/falha controlada.
- `docs/migracao/RELATORIO_ETAPA_12B1.md` — este relatório.

## Limitações e prontidão

- A conversão executada continua limitada às 12 amostras aprovadas e à amostra adicional de 47.1; não se converteu a árvore inteira.
- A associação de rubrica de projeto depende dos aliases de manifesto conhecidos. Um alias não reconhecido falha em vez de inferir o alvo.
- O texto completo de origem do arquivo de flashcards é mantido em cada cartão derivado; isso é fiel, mas repete bytes no contrato e pode aumentar seu tamanho.
- Links Obsidian continuam pendentes até que a raiz do vault seja informada. `47.2` e `47.3` permanecem pendências editoriais sem destinos criados.
- Respostas corretas não podem ser expostas diretamente ao aluno; a política de apresentação e correção continua pendente e o importador/renderer não foi adaptado.
- O novo contrato não foi testado contra banco, API ou UI de produção.

**Recomendação:** pronto para revisão técnica e para uma próxima etapa de dry-run ampliado com cobertura de todos os tipos e relatórios por bloco. **Não recomendado ainda para conversão integral ou importação** até a homologação do contrato 1.1, a revisão dos tipos restantes e a definição da proteção/revelação de gabaritos.
