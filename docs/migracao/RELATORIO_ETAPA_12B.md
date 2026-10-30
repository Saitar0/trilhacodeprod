# Etapa 12B — conversor Markdown para contrato intermediário

**Estado:** implementado e testado em amostras representativas; não integrado à plataforma.  
**Base examinada:** branch `migracao-estrutura`, commit `147dc68b81169f66b0ba3802fa2f26e5130923a3`.  
**Contrato utilizado:** `trilhacode.intermediate/1.0`, implementado em `backend/curriculum_contract/` na Etapa 12A.

## Resultado

Foi implementado um conversor isolado que lê manifestos aprovados e arquivos Markdown já migrados, constrói os modelos Pydantic da Etapa 12A, valida relações e proveniência e permite serialização determinística. O conversor não grava dentro do repositório, não toca no JSON legado e não acessa importador, frontend ou MongoDB.

O pré-voo confirmou o worktree e a branch esperados, HEAD `147dc68b81169f66b0ba3802fa2f26e5130923a3`, nenhum arquivo rastreado alterado e nenhum conteúdo staged. Os 2.890 arquivos migrados e 133 fontes Markdown continuam presentes. O JSON legado manteve SHA-256 `43125C5902168DEF6359E514AD80602A1F7579157E1A0BB16F1F2212EE4C18E7`. Os artefatos locais não rastreados preexistentes foram preservados.

## Arquivos da Etapa 12B

| Caminho | Uso |
|---|---|
| `backend/curriculum_contract/converter.py` | Conversor fail-closed baseado nos modelos e validadores 12A. |
| `backend/unit_tests/test_curriculum_markdown_converter.py` | Testes com amostras reais e fixtures temporárias para erros. |
| `docs/migracao/RELATORIO_ETAPA_12B.md` | Registro desta implementação, validação e limitações. |

Os outros arquivos do pacote, os testes `test_curriculum_contract.py` e o relatório 12A já existiam como artefatos locais não rastreados antes desta etapa; não foram substituídos.

## Amostras executadas

O conversor leu os índices da fase necessários à hierarquia, mas só converteu o conteúdo das unidades selecionadas. Os contratos e mapas de origem resultantes foram escritos em um diretório temporário do sistema e removidos ao final da execução.

| Fase | Unidades de conteúdo convertidas | Arquivos de origem mapeados |
|---|---|---:|
| 1 | 1.1 | 37 |
| 2 | 4.1 | 27 |
| 3 | 8.5 | 29 |
| 4 | 16.2 | 33 |
| 5 | 24.3 | 36 |
| 6 | 31.2 | 32 |
| 7 | 36.2 | 28 |
| 8 | 37.1, 39.2 | 27 |
| 9 | 46.1, 46.2 | 55 |
| 10 | 52.1 | 28 |
| **Total** | **12 unidades** | **332** |

As amostras cobrem conteúdo convencional, teoria e código, quizzes e gabaritos, prática e solução, flashcards, prática compartilhada, referências, projeto com entregas e aceite, projeto sem marcos formais, rubricas e limiares, escolha de stack e pendências editoriais. A amostra bloqueante 47.1 foi executada separadamente e não foi serializada.

Nas dez conversões válidas foram produzidos em memória e serializados em temporário 572 nós hierárquicos, 243 blocos, seis projetos e 48 colocações compartilhadas. Esses totais incluem nós de hierarquia lidos dos manifestos/índices das fases; não significam conversão integral das fases.

## Tipos e mapeamentos

O conversor reutiliza os modelos 12A: objetivo, resumo, conclusão, teoria, quiz, `answer_key`, prática, solução, feedback, flashcard, checklist, critério de aceite, rubrica e referência. Também representa relações curriculares, colocações compartilhadas, escopo/projeto, entregas, marcos, variações, proveniência, pendências editoriais e hashes SHA-256.

Os mapeamentos de origem são um por arquivo de origem, com caminhos, ID original, tipo, SHA-256, destinos no contrato e normalizações registradas. A verificação de proveniência recalcula o hash dos bytes lidos. IDs gerados para questão e resposta derivam do ID do arquivo e do ID literal do item; o validador detecta colisões. A ordem vem dos metadados de origem, com faixas tipadas para manter determinismo sem colidir blocos de naturezas diferentes.

Quizzes e respostas são objetos separados e ligados por referências recíprocas. As chaves não são convertidas para `theory_text`. A serialização do contrato é conteúdo de autoria e contém gabaritos; não deve ser enviada diretamente ao aluno. O conversor não implementa tentativas, correção de resposta nem política de revelação.

Para conteúdo compartilhado existe um bloco canônico e uma colocação por assunto consumidor. O progresso permanece `undecided`, sem escolher uma política de produto. Práticas compartilhadas não são copiadas por assunto.

## Fidelidade e normalizações

Os corpos Markdown de teoria, práticas, soluções, quizzes e etapas de projeto permanecem associados à proveniência e ao hash integral do arquivo de origem. Os testes conferem corpos de teoria/solução, cercas e conteúdo de código, reconstrução dos arquivos de questões e referências. As respostas são separadas apenas em limites reconhecidos literalmente; limites não reconhecidos produzem erro estruturado, sem tentativa de adivinhação.

Normalizações estruturais explícitas:

1. O frontmatter é convertido em campos tipados e metadados de origem; o corpo Markdown não é reescrito por essa operação.
2. Questões em arquivos compostos são segmentadas pelos marcadores literais e `itens_origem` do manifesto; as respostas correspondentes tornam-se `AnswerKeyBlock` com referência à questão.
3. Campos literais `Resposta` e marcadores numerados são representados em `expected_answer` e `explanation`; a normalização é registrada no mapeamento e o SHA preserva a trilha para os bytes originais.
4. Linhas de referências externas viram referências tipadas, mantendo a linha original em `citation`/`raw_text`. Wikilinks e links locais sem destino contratual são mantidos literalmente como referência pendente.
5. Tabelas e listas de rubrica são representadas por dimensões e descritores tipados; prosa explicativa fora da tabela é ligada como feedback quando o modelo permite. O arquivo original completo continua identificado pelo hash.

O teste da unidade 46.2 confirmou as opções `42.1`, `43.1`, `44.1` e `45.1` vindas de `stack_opcoes`, `stack_mode: alternativa`, `escolha_do_aluno: true` e `stack_selecionada: null`. As opções ficam em `ProjectSpec.stack_options`; os campos contextuais não previstos como campos próprios do modelo são preservados em `source_metadata.project_manifest`.

## Diagnósticos e limitações encontradas

A amostra 47.1 produz o erro bloqueante `RUBRIC_TARGET_AMBIGUOUS`: o arquivo R00 nomeia múltiplos alvos, mas `RubricBlock` 1.0 aceita um único `target_ref`. O contrato parcial mantém as pendências literais para 47.2 e 47.3; `canonical_json()` recusa serializar uma conversão com erro. Não foram criados destinos.

As dez amostras válidas geraram 47 avisos estruturados: 11 critérios de conclusão representados como `ConclusionBlock`, 14 pendências da raiz Obsidian, dois mapeamentos de decisões/cenários para checklist e 20 textos de etapas de projeto preservados como `PracticeBlock` referenciado por entrega/marco. Esses casos não são silenciosos, mas exigem revisão antes de qualquer importação.

Limitações semânticas do contrato atual:

- Não há tipo próprio para critério de conclusão de unidade, decisões de projeto ou cenários de projeto; os dois últimos são preservados item a item como checklist com aviso.
- Entrega/marco não possui campo textual; o enunciado literal da etapa é mantido como bloco de prática referenciado e gera aviso. A futura integração precisa validar se essa apresentação representa corretamente o produto.
- `RubricBlock` possui um único alvo. Rúbricas que cobrem vários alvos, como 47.1/R00, bloqueiam a conversão até uma extensão aprovada do contrato.
- `ProjectSpec` preserva modo de stack, escolha do aluno e opção selecionada no mapa de metadados, mas o modelo 1.0 não tem campos próprios para `stack_mode` e `escolha_do_aluno`.
- O contrato não resolve progresso por contexto, proteção/revelação de respostas nem destinos locais editoriais. Wikilinks continuam pendentes enquanto a raiz do vault não for confirmada.
- Referências a `47.2`/`47.3` permanecem pendências editoriais; nenhuma unidade é fabricada.

Tipos de fonte desconhecidos e frontmatter inválido falham com diagnósticos bloqueantes. Não há fallback genérico para teoria.

## Testes e verificações

Executados em Python 3.11 com dependências temporárias via `uv`; nenhum arquivo de dependências foi alterado.

| Verificação | Resultado |
|---|---|
| `pytest unit_tests/test_curriculum_markdown_converter.py unit_tests/test_curriculum_contract.py unit_tests/test_import_payload_shape.py -q` | **65 passaram**: 22 testes do conversor, 23 da Etapa 12A e 20 de regressão existente. |
| Ruff `check` no pacote e testes 12B | Aprovado. |
| Ruff `format --check` no pacote e testes 12B | Aprovado; arquivos já formatados. |
| mypy no pacote `curriculum_contract` e no teste 12B, com Python 3.11 e stubs PyYAML | Aprovado; sem problemas nos cinco arquivos verificados. |
| Compilação dos módulos do pacote e teste 12B | Aprovada; cinco arquivos compilados. |
| Inspeção da serialização temporária | Dez contratos válidos serializados deterministicamente; o caso 47.1 foi bloqueado e não serializado. |

Uma execução adicional de mypy que incluiu o teste preexistente `test_curriculum_contract.py` apontou oito problemas de narrowing/união nesse arquivo de teste. Ele não foi modificado; seus 23 testes passam. A verificação final de mypy foi executada no pacote e no novo teste do conversor, não nesse módulo de teste anterior.

Não foram executados o importador, conversão integral, frontend, banco ou testes de integração com MongoDB.

## Recomendação para a Etapa 12C

O conversor está pronto para revisão de engenharia como ferramenta de amostragem/dry-run, mas **não está pronto para converter integralmente as dez fases nem para produzir payload de importação**. Antes disso, revisar as aproximações de conclusão, etapas, decisões/cenários e metadados de stack; decidir como representar rubricas multi-alvo; avaliar todos os tipos e limites com amostras aprovadas; e manter respostas protegidas fora de qualquer payload de aluno. A conversão integral deve ocorrer somente após uma etapa de dry-run com inventário completo, destino temporário, relatório por bloco e aprovação específica.

## Estado de escopo

Não houve conversão integral, geração ou alteração do JSON legado, importação, acesso a MongoDB, mudança de frontend ou schema de produção, alteração das árvores migradas, commit ou push. O trabalho aguarda homologação antes da próxima etapa.
