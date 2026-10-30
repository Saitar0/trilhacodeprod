# Etapa 12A — contrato intermediário, validadores e testes

**Estado:** implementado isoladamente; não integrado ao importador ou à plataforma.  
**Base examinada:** `migracao-estrutura` em `147dc68b81169f66b0ba3802fa2f26e5130923a3`.  
**Contrato:** `trilhacode.intermediate/1.0`.

## Resultado

Foi criado um pacote Pydantic independente do schema de produção. Ele valida uma representação curricular tipada e pode serializá-la de forma determinística. Não lê nem grava arquivos de curso, JSON legado ou MongoDB. A validação de hashes recebe bytes fornecidos pelo chamador; não acessa o caminho de origem.

O pré-voo confirmou a branch e o commit-base esperados, índice vazio e nenhum arquivo rastreado modificado. Os artefatos locais não rastreados preexistentes foram preservados. As dez árvores migradas permanecem com 2.890 arquivos. O JSON legado permaneceu inalterado; SHA-256 verificado: `43125C5902168DEF6359E514AD80602A1F7579157E1A0BB16F1F2212EE4C18E7`.

## Arquivos criados

| Arquivo | Responsabilidade |
|---|---|
| `backend/curriculum_contract/models.py` | Modelos Pydantic estritos, discriminador de tipos, JSON Schema, projeção de quiz para apresentação ao aluno e serialização canônica. |
| `backend/curriculum_contract/validation.py` | Validação semântica, diagnósticos tipados, verificação de SHA-256 fornecido e classificação pura de diferenças candidatas. |
| `backend/curriculum_contract/__init__.py` | Interface pública do pacote isolado. |
| `backend/unit_tests/test_curriculum_contract.py` | Testes unitários sem banco de dados. |
| `docs/migracao/RELATORIO_ETAPA_12A.md` | Este relatório. |

## Schemas implementados

- Envelope com versão, revisão da fonte, manifesto e versão do conversor.
- Nós `phase`, `module`, `submodule` e `topic`, com IDs estáveis `f1`–`f10`, ordem, metadados originais, tags e proveniência.
- Relações curriculares tipadas e marcadas como obrigatórias ou informativas.
- Blocos discriminados: objetivo, resumo, conclusão, teoria/microtópico, quiz, `answer_key`, prática, solução, feedback, flashcard, checklist, critério de aceite, rubrica e referência.
- Bloco compartilhado canônico e colocações por assunto, cada qual com ordem e política de progresso (`undecided`, `per_context` ou `shared_global`). A política indefinida produz informação, não escolhe um comportamento de produto.
- Projetos com escopo, entregas, marcos formais, variações, opções/seleção de stack, checklists, rubricas e critérios ligados ao destino correto. Entregas e marcos são listas separadas; projetos sem marcos formais continuam válidos sem marcos artificiais.
- Referências externas, internas, Obsidian e editoriais; pendências explícitas para referências sem destino ou decisões editoriais não resolvidas.
- Proveniência com caminho relativo POSIX e SHA-256; helper para comparar o hash com bytes fornecidos.

`json_schema()` expõe o JSON Schema derivado do contrato. `canonical_json()` ordena deterministicamente nós, blocos, relações, colocações, projetos, entregas, marcos e variações. A ordenação curricular usa `order`; IDs não são derivados de títulos ou posição.

## Validadores e diagnósticos

`validate_contract()` retorna `ValidationReport` e diagnósticos com `code`, `severity`, `source_file`, `entity_ref`, `field`, `reference`, `message` e `remediation`.

As regras bloqueantes cobrem schema/tipo desconhecido, IDs repetidos, pais inexistentes, hierarquia e pré-requisitos cíclicos, ordens duplicadas, referências órfãs, pares quiz–gabarito ausentes/ambíguos/incompatíveis, prática sem destino de solução, colocações compartilhadas inválidas ou repetidas, escalas e limiares fora da faixa, critérios associados a entrega/marco incorretos, projeto que contradiz a presença de entregas/marcos formais, seleção de stack fora das opções, e hashes/metadados de origem inválidos. A serialização JSON estrita também rejeita valores não serializáveis.

Referências editoriais bloqueantes são erros. Pendências não bloqueantes de Obsidian geram aviso; outras pendências editoriais geram informação. O validador preserva a referência literal e não fabrica destinos para `47.2`/`47.3` ou wikilinks.

## Compatibilidade verificada com o código atual

Evidências consultadas:

- `backend/constants.py`: hierarquia padrão `phase → module → submodule → topic`.
- `backend/schemas/content.py`: `NodeIn` e `BlockIn` usam modelos genéricos; um bloco tem `node_id`, `type`, `data` e `status`.
- `backend/seed.py`: catálogo atual inclui, entre outros, `theory_text`, `summary`, `checklist`, `exercise_objective`, `exercise_open`, `practical_challenge`, `quiz`, `flashcard`, `code_snippet`, `video_embed`, `instructor_note`, `review`, `supplementary` e `reference`.
- `backend/services/imports.py` e `backend/import_payload.py`: importação legada recebe `track/options/nodes/relations`, valida tipo contra o catálogo cadastrado e não tem `schema_version` do contrato intermediário.
- `backend/services/nodes.py` e `frontend/src/components/blocks/BlockRendererParts.tsx`: o renderer de quiz lê `correct_index` no cliente, enquanto a resposta de leitura do aluno remove `answer`, `correct_index` e `explanation`. O teste existente `backend/tests/test_phase2.py` cobre a ocultação. `backend/services/progress.py` registra estado/dados enviados pelo cliente; não é uma correção autoritativa de quiz.
- `backend/services/submissions.py`: submissões dependem de capabilities e representam correção manual; isso não equivale ao gabarito editorial de quiz.

O contrato intermediário, portanto, **não é aceito diretamente** pelo importador atual. Não foi alterado nenhum schema de produção, renderer, endpoint ou importador.

## Gabaritos e proteção de respostas

`QuizBlock` e `AnswerKeyBlock` têm IDs próprios e referências recíprocas; o gabarito separa resposta e explicação do conteúdo apresentado. `student_quiz_view()` constrói uma projeção com enunciado e opções, sem referência nem conteúdo do gabarito. Isso é uma primitiva de contrato, não uma rota nem uma política de revelação implementada.

O contrato completo é conteúdo de autoria e **não deve ser entregue diretamente ao cliente aluno**. A política de tentativa, correção no servidor e momento/forma de revelar resposta e explicação segue pendente. Até a tarefa separada de extensão do importador e renderer, permanece válida a limitação aprovada: o JSON legado conserva os gabaritos em `theory_text`; esta etapa não tocou nele.

## Conteúdo compartilhado e reimportação

O conteúdo compartilhado existe uma vez como bloco canônico; cada `SharedPlacement` referencia esse bloco e o assunto consumidor. O validador rejeita bloco/assunto ausente, placement repetido, bloco compartilhado sem placement e colisão de ordem no mesmo contexto. O escopo de progresso fica explicitamente indefinido até decisão de produto.

`classify_changes()` é uma função pura que, recebidos hashes candidatos e baseline, classifica `new`, `unchanged`, `modified`, `conflict` ou `absent`. Não consulta MongoDB, não escreve registros e fixa `deletion_authorized: false`, inclusive quando a origem está ausente. Não há mecanismo de importação ou rollback implementado nesta etapa.

## Verificações executadas

Executadas em Python 3.11 com as versões do backend/dev declaradas pelo repositório: Pydantic 2.13.5, pytest 9.1.1, Ruff 0.14.3 e mypy 2.4.0. As dependências foram resolvidas em ambiente temporário do `uv`, sem alterar arquivos de dependência do projeto.

| Verificação | Resultado |
|---|---|
| `pytest unit_tests/test_curriculum_contract.py -q` | 23 passaram. |
| `pytest unit_tests/test_import_payload_shape.py -q` | 20 testes de regressão existentes passaram; importador não foi executado. |
| `ruff check curriculum_contract unit_tests/test_curriculum_contract.py` | Aprovado. |
| `ruff format --check curriculum_contract unit_tests/test_curriculum_contract.py` | Aprovado; todos os arquivos já formatados. |
| `mypy curriculum_contract` | Aprovado; sem erros nos 3 módulos do pacote. |
| `python -m py_compile` dos módulos do pacote | Aprovado. |
| Testes/validação envolvendo MongoDB | Não executados; o contrato é puro e esta etapa proíbe alteração ou uso de banco real. |

Os 23 testes cobrem contrato válido, schema inválido, IDs repetidos, pai ausente, ciclo, tipo desconhecido, quiz sem gabarito, associação errada, referências/colocações compartilhadas, escala e limiar de rubrica, projeto sem marcos formais, projeto com marco/variação tipados, proveniência ausente, hash inválido, caminho de manifesto inseguro, pendência Obsidian, ordem canônica, serialização, projeção sem chave e as cinco classificações de mudança sem autorização de exclusão.

## Pendências e riscos para a Etapa 12B

1. Aprovar a política de tentativas e revelação do quiz; implementar correção autoritativa no servidor antes de publicar chaves.
2. Estender importador e renderer para tipos/campos não suportados (`answer_key`, solução protegida, rubricas, aceite formal, colocações compartilhadas e semântica completa de projetos). A arquitetura e o contrato não alteram esse comportamento.
3. Decidir progresso por colocação ou compartilhado para conteúdo em múltiplos assuntos.
4. Resolver destino dos wikilinks após confirmação da raiz do vault; resolver editorialmente referências sem destino, incluindo `47.2`/`47.3`, antes de prometer navegação.
5. Definir o tratamento de colisões locais, política de publicação/status e migração de dados de projeto/variações.
6. Criar conversor, dry-run e importação experimental apenas em tarefa autorizada posterior. Ausência de conteúdo no candidato não deve excluir registros automaticamente.

## Estado de escopo

Não houve conversão das 2.890 fontes migradas, alteração do JSON, importação, acesso ou escrita em MongoDB, mudança em código de produção, alteração das fases homologadas, commit ou push. Esta entrega aguarda homologação antes da Etapa 12B.
