# Matriz de segurança — persistência de atividades 14F

| Risco | Controle implementado | Evidência de teste | Limite/pendência |
|---|---|---|---|
| Gabarito retornado em leitura pública | Coleção pública separada; allowlist explícita de campos; não contém payload privado nem hash de conteúdo integral | `test_storage_splits_public_private_and_audit_for_all_six_types`; `test_idempotent_write_and_public_private_reads_use_separate_collections` | Não existe endpoint de aluno ligado a esta coleção; consulta HTTP e logs da aplicação não foram exercitados |
| Mass assignment de campos privados | Modelo público Pydantic estrito e distinto do modelo privado | `test_public_stored_schema_rejects_private_fields` | Validado em modelo local, não em API |
| Leitura privada sem autorização | Reutiliza `permissions.has_permission`; exige `submissions.grade`; ausência/role inválido falha fechada | `test_store_authentication_reuses_platform_permissions_and_denies_students`; leitura privada em teste de repositório fake | RBAC de coleção Mongo ainda precisa de configuração real; nenhuma rota foi criada |
| Escrita sem permissão editorial | `content.write` exigido no método de gravação | Teste de permissão da camada | Não há endpoint administrativo; controle HTTP não foi testado |
| Reutilização de versão com conteúdo divergente | Hash canônico privado + índice único; não atualiza. Revisões exigem `expected_version_id` e um head avança via compare-and-swap dentro da transação | `test_private_answer_change_creates_a_distinct_content_fingerprint`; testes de revisão com base explícita e conflito entre revisões concorrentes | Concorrência, índice e compare-and-swap foram simulados em fake, não comprovados no Mongo desta máquina |
| Par público sem par privado, ou vice-versa | Quatro gravações (público, privado, evento e head) em transação; leitura privada confere o companheiro e o tipo público | Teste de rollback em fake; teste de integridade de par no repositório | Transação Mongo real não executada: falta URI de replica set descartável |
| Escrita parcial em standalone | Não há fallback sem transação; erros de transação são convertidos em bloqueio explícito | Teste fake injeta falha após as primeiras inserções | Necessita homologação em replica set descartável |
| Corrida em reexecução idempotente | Índices únicos e consulta por hash privado; versão antiga não sofre overwrite | Teste concorrente fake e replay idêntico | Não prova semântica de concorrência Mongo entre processos |
| Exposição de hash que permita inferir gabarito | Hash integral e hash da chave ficam somente no documento privado; write result e evento não os incluem | Inspeção de projeções e assertivas de payload público | Metadados do Mongo e telemetria externa não foram testados |
| Publicação acidental | Nenhuma rota/integração; estado `published` recusado; `publishable` é apenas status editorial | `test_published_records_cannot_enter_draft_store`; `test_publishable_is_only_an_editorial_label_not_operational_publication` | Não há controle de ativação, pois o módulo não está ligado à aplicação |
| Alteração retroativa de tentativas publicadas | Store não toca `quiz_versions` ou `quiz_progress`; grava versões editoriais imutáveis separadas | Inspeção de código e testes unitários; regressão do grader executada | Não foi possível reconciliar com registros existentes sem snapshot autorizado |
| Credenciais de ambiente testam DB errado | Teste Mongo exige URI própria, host loopback, porta, replica set, confirmação de descarte e `hello` antes do DB | Teste opcional foi skip por falta de URI; não tentou fallback a localhost | Executar em runner local/CI descartável e registrar versão/topologia |
| Conteúdo dos logs inclui resposta | Nenhuma chamada de logging no repositório; erros têm mensagens estáticas; repr dos campos privados omitido | Inspeção estática e modelos privados | Logging/telemetria do serviço completo não conectado nem testado |

## Perfis e separação

O storage separa conteúdo answer-key-free de material privado por coleção. O código usa as permissões existentes `content.write`, `content.read` e `submissions.grade`, sem adicionar permissões globais. Isso protege o caminho de serviço; não substitui RBAC Mongo. Antes de integrar, credenciais públicas devem ser impossibilitadas de consultar a coleção privada e testes HTTP devem confirmar a allowlist.

## Estado da validação

**Unitário:** executado com dados sintéticos e repositório fake; não é prova de atomicidade Mongo.

**Mongo descartável:** não executado. `TRILHACODE_TYPED_ACTIVITY_MONGO_TEST_URI` não estava configurada, Docker daemon indisponível e `mongod` não instalado. O teste de integração opcional ficou skipped. Nenhuma instância Mongo foi contactada.

**Produção:** não acessada; nenhuma migration, índice, publicação ou gravação operacional foi executada.
