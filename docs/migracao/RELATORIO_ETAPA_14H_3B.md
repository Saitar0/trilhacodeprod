# Relatório — Etapa 14H.3B

## Resultado

Foi implementada uma camada editorial restrita e isolada para blocos compartilhados, colocações curriculares e projetos. Ela reutiliza os modelos Pydantic do contrato intermediário, mantém referências curriculares separadas dos identificadores MongoDB e não foi conectada às rotas, ao importador, à publicação, ao progresso, aos quizzes operacionais ou ao frontend.

A persistência aceita somente revisões de blocos em estado `draft`; conteúdo publicado ou arquivado é recusado. Colocações continuam com `progress_scope: undecided`. Projetos continuam agregados, com entregas e marcos em listas distintas; seleção de stack e variantes são recusadas enquanto D11 estiver adiada.

## Arquivos desta etapa

- `backend/curriculum_contract/editorial_persistence.py` — schemas persistidos, validação, autorização, índices explícitos e repositório assíncrono.
- `backend/unit_tests/test_editorial_persistence.py` — testes unitários sem banco.
- `backend/unit_tests/test_editorial_persistence_mongodb.py` — testes opt-in que exigem URI e marcadores explícitos de MongoDB descartável.
- `docs/migracao/CONTRATO_PERSISTENCIA_EDITORIAL_14H_3B.md` — contrato físico e semântica das operações.
- `docs/migracao/HOMOLOGACAO_MONGODB_14H_3B.md` — evidências do ambiente descartável e seus limites.
- Este relatório.

Os demais arquivos modificados ou não rastreados já estavam no worktree antes desta etapa e foram preservados. O bundle curricular aparece como modificado no Git por trabalho local preexistente; seu hash antes e depois desta etapa foi o SHA-256 aprovado informado abaixo.

## Modelo implementado

O repositório usa cinco coleções com prefixo `curriculum_editorial_`:

1. `heads`: uma identidade estável por bloco, colocação ou projeto, identidade imutável e ponteiro para a revisão atual.
2. `revisions`: metadados imutáveis, número sequencial, hash do conteúdo e proveniência editorial.
3. `private_payloads`: payload completo de cada revisão; não existe projeção pública neste repositório.
4. `events`: evento mínimo de criação de revisão, sem corpo, gabarito ou explicação.
5. `operations`: reserva de idempotência e resultado reconciliável.

Bloco e colocação são identidades distintas. A colocação armazena somente suas referências, ordem, proveniência e escopo; não contém uma cópia do bloco. Projetos guardam uma revisão agregada com entregas e marcos separados. Referências de bloco existentes são fixadas ao `revision_id`, número e hash exatos observados na transação. Referências ausentes ficam marcadas como `unresolved` e permanecem apenas no armazenamento editorial restrito.

## Integridade, concorrência e recuperação

Hashes usam JSON determinístico UTF-8, com chaves ordenadas, sem espaços variáveis e preservação da ordem de arrays. As revisões recebem IDs derivados da referência da operação; os ObjectIds, gerados pelo MongoDB, não participam da identidade curricular nem dos hashes.

Operações mutáveis exigem autorização explícita, chave de idempotência e o par esperado de revisão ID/número. O par é verificado na transação; atualização do head usa compare-and-swap. Uma chave já confirmada com o mesmo comando retorna a revisão anterior sem duplicá-la. A mesma chave com outro comando é conflito. Reservas com resultado não comprovado ficam `unknown`/`pending`; não há nova gravação automática. Uma transação abortada de forma conhecida fica `not_committed`/`retryable` e só aceita repetição do mesmo comando.

Criação ou revisão grava payload, metadados, evento, head e confirmação da operação em uma transação MongoDB com snapshot, majority write concern e leitura primária. A reserva idempotente inicial é uma escrita de documento único fora da transação para que um retry possa localizar a intenção após interrupção; a reserva não representa sucesso. Sem suporte a transações, a operação falha e a reserva é marcada como não confirmada quando isso puder ser comprovado.

## Autorização e privacidade

O autorizador é fail-closed: sem autorizador ou em caso de exceção, a operação é negada. Capacidades próprias `curriculum.editorial.*` não reutilizam permissões operacionais como `content.write`, `content.publish` ou `submissions.grade`. Leitura de revisão completa requer leitura editorial, leitura de conteúdo e, para blocos/projetos, leitura privada. Histórico e criação de índices têm capacidades distintas.

Payloads e campos privados ficam em coleção separada e modelos usam `repr=False` para corpos. Não há serializador de aluno, endpoint, publicação ou projeção pública. Os testes de RBAC demonstram que uma credencial de metadados sem privilégio da coleção privada não consegue ler ou escrever essa coleção. A credencial editorial de serviço usada para operações transacionais possui os privilégios mínimos necessários por coleção, incluindo leitura de payload para validação de integridade; ela deve continuar restrita ao processo editorial futuro e não deve ser reutilizada por clientes.

## Índices

`ensure_indexes` é explícito, exige `curriculum.editorial.admin` e não roda implicitamente ao gravar. Índices efetivamente criados no banco descartável:

- head único por `(entity_kind, entity_ref)`;
- par `(identity.block_ref, identity.subject_ref)` único para colocações;
- revisão única por `(entity_kind, entity_ref, revision_no)` e por `revision_id`;
- histórico de revisões por entidade/data;
- payload único por `revision_id`;
- evento único por `operation_ref` e índice de histórico;
- operação única por `operation_ref` e índice de histórico.

Não há TTL. Nenhum índice foi aplicado em banco preexistente ou operacional.

## Decisões respeitadas

Implementadas somente as decisões aprovadas: D01–D07 e D17. Permanecem pendentes D08–D16 e D18. Em particular, não há progresso por bloco/colocação, política de publicação, retirada de colocação, stack selecionada, checklist por aluno, submissões, evidências, avaliação de projeto, TTL, exclusão automática ou reconciliação de progresso legado.

## Validações executadas

Ambiente: Windows, Python 3.13, Pydantic 2.13.5, PyMongo 4.17.0, MongoDB 9.0.2.

- `py -3.13 -m pytest backend/unit_tests/test_editorial_persistence.py -q`: **21 passed**, incluindo preservação de campo opcional ausente.
- `py -3.13 -m pytest backend/unit_tests/test_editorial_persistence_mongodb.py backend/unit_tests/test_typed_activity_persistence_mongodb.py -q --tb=short`, com URIs explícitas e marcadores descartáveis: **9 passed** (4 editoriais, incluindo standalone; 5 regressões da 14F).
- `py -3.13 -m pytest backend/unit_tests/test_editorial_persistence.py backend/unit_tests/test_typed_activity_persistence.py backend/unit_tests/test_typed_activities.py backend/unit_tests/test_shared_content_projection.py backend/unit_tests/test_project_projection.py backend/unit_tests/test_curriculum_contract.py backend/unit_tests/test_curriculum_import_adapter.py backend/unit_tests/test_curriculum_bulk_import.py backend/unit_tests/test_experimental_quiz_converter.py backend/unit_tests/test_quiz_api_contracts.py backend/unit_tests/test_quiz_grading.py backend/tests/test_quizzes.py backend/tests/test_typed_prerequisites.py -q`: **267 passed**.
- `ruff check backend/curriculum_contract/editorial_persistence.py backend/unit_tests/test_editorial_persistence.py backend/unit_tests/test_editorial_persistence_mongodb.py`: aprovado.
- `ruff format --check backend/curriculum_contract/editorial_persistence.py backend/unit_tests/test_editorial_persistence.py backend/unit_tests/test_editorial_persistence_mongodb.py`: 3 arquivos já formatados.
- `py -3.13 -m mypy --explicit-package-bases --follow-imports=silent curriculum_contract/editorial_persistence.py unit_tests/test_editorial_persistence.py unit_tests/test_editorial_persistence_mongodb.py` (executado em `backend/`): sem problemas em 3 arquivos.
- `py -3.13 -m py_compile backend/curriculum_contract/editorial_persistence.py backend/unit_tests/test_editorial_persistence.py backend/unit_tests/test_editorial_persistence_mongodb.py`: aprovado.
- `git diff --check`: código de saída 0; Git emitiu somente aviso de normalização LF/CRLF do JSON já modificado antes da etapa. O verificador adicional de whitespace para os seis arquivos novos não encontrou espaços finais.

Durante a validação, foram corrigidos defeitos no harness de teste (proxy de falhas após `with_options`, permissões de leitura de índices e setup de índices local por instância) e erros de tipagem/teste encontrados pela primeira execução de mypy. Os resultados acima são as execuções finais após as correções.

Hash do bundle antes e depois: `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.

## Limites e parecer

Os testes MongoDB demonstram transações, rollback, CAS, concorrência, idempotência, índices e RBAC no MongoDB 9.0.2 local. O replica set tinha um único membro; não prova eleição, failover, disponibilidade distribuída, configuração nem permissões de produção. O teste standalone demonstra recusa a transações quando o servidor não as suporta.

Os processos desta execução foram encerrados e as portas exclusivas estão fechadas. A remoção dos diretórios temporários não foi permitida pela política de execução; os quatro caminhos remanescentes e a necessidade de remoção manual estão descritos em `HOMOLOGACAO_MONGODB_14H_3B.md`.

A persistência editorial está validada para continuar em homologação isolada. Não está pronta para produção: não há implantação, integração operacional, importação, publicação, configuração de produção ou política de produto além das aprovações listadas. A próxima etapa exige revisão humana deste código e decisão explícita antes de qualquer integração. A homologação fica tecnicamente parcial até a remoção manual dos temporários.
