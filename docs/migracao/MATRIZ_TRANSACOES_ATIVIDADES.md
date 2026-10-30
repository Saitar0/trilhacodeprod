# Matriz de transações — persistência de atividades 14F

## Fluxos e limites

| Fluxo | Operações e sessão | Controle | Evidência nesta etapa |
|---|---|---|---|
| Preparação de índices | `ensure_indexes()` fora da transação | DDL explícito, índices nomeados; não é parte atômica do snapshot | Definições inspecionadas; não criados em Mongo real |
| Replay idêntico | Busca pelo hash privado fora da transação; valida par público/privado, identidade e hashes | Retorna `unchanged`; não grava | Coberto por fake; não executado em Mongo |
| Primeira versão | Na sessão: lê head e histórico nas três coleções; insere público, privado, evento e head | `with_transaction`; head único; qualquer erro aborta a callback | Caminho estático confirmado; transação real não executada |
| Revisão | Na sessão: valida head e par atual; insere público, privado e evento; CAS do head | `expected_version_id`, filtro por versão atual e `matched_count == 1` | Fake e teste opt-in; Mongo não executado |
| Revisão concorrente obsoleta | Leitura e CAS na mesma sessão | Apenas uma alteração baseada no head pode vencer; demais resultam em conflito | Fake aprovado; corrida Mongo não executada |
| Recuperação após erro | Busca por hash após duplicidade; novo replay do mesmo conteúdo | Não repete escrita com nova identidade; resultado incerto é classificado separadamente | Replay incerto simulado no fake; commit Mongo incerto não exercitado |
| Leitura pública | Somente coleção pública, projeção allowlist | Requer `content.read`; não há rota de aluno ligada à coleção | Teste de repositório fake; RBAC Mongo não comprovado |
| Leitura privada | Coleção privada com projeção explícita e validação do companheiro público | Requer `submissions.grade` no serviço | Teste fake; credenciais por coleção não testadas |

Todas as leituras que decidem a inserção/revisão e todas as gravações do fluxo transacional recebem a mesma `session`. O lookup inicial de conteúdo idêntico ocorre fora da transação; ele só pode retornar `unchanged` depois de revalidar o par. O lookup depois de duplicidade também é somente leitura.

## Índices declarados no código

| Coleção | Índice | Restrição/uso | Estado real |
|---|---|---|---|
| `typed_activity_public_versions` | `one_typed_activity_public_version` em `(activity_ref, version_id)` | Único | Não criado/verificado no Mongo |
| `typed_activity_public_versions` | `typed_activity_public_version_history` em `(activity_ref, created_at desc)` | Histórico | Não criado/verificado no Mongo |
| `typed_activity_private_versions` | `one_typed_activity_private_version` em `(activity_ref, version_id)` | Único | Não criado/verificado no Mongo |
| `typed_activity_private_versions` | `one_typed_activity_content_revision` em `(activity_ref, private_content_sha256)` | Unicidade para replay idempotente | Não criado/verificado no Mongo |
| `typed_activity_version_events` | `one_typed_activity_creation_event` em `(activity_ref, version_id, event_type)` | Único | Não criado/verificado no Mongo |
| `typed_activity_heads` | `one_typed_activity_current_head` em `(activity_ref)` | Um head por atividade | Não criado/verificado no Mongo |

`_id` também é definido para versões público/privada e head. A definição no código não comprova a existência, unicidade sob corrida ou compatibilidade dos índices em um servidor real.

## Matriz de falhas

| Ponto de falha | Tratamento no código | Validação fake | Validação Mongo nesta etapa |
|---|---|---|---|
| Antes de iniciar sessão | Erro classificado como requisito de transação quando o servidor reporta ausência de suporte; nenhuma coleção recebe versão | Teste com `OperationFailure` code 20 | Não executada |
| Depois da primeira escrita staged | Driver deve abortar a transação; não existe fallback fora dela | Falha injetada no fake | Teste opt-in foi preparado; não executado |
| Depois das linhas público/privado/evento e antes do head | Transação deve abortar; head e versão anterior devem continuar intactos | A lógica fake cobre falha geral; o teste real de revisão foi preparado | Não executada |
| Conflito de CAS | Aborta a transação e retorna conflito; não avança o head stale | Teste de duas revisões no fake | Teste opt-in concorrente preparado; não executado |
| `UnknownTransactionCommitResult` | `ActivityTransactionOutcomeUnknownError`; orientar replay do mesmo conteúdo | Simulação de commit persistido com resposta perdida e replay `unchanged` | Não executada; sem falha de commit real |
| Erro PyMongo não classificado como falta de transação | `ActivityTransactionFailedError`; replay idêntico é a forma segura de reconciliar | Falha fake após staged write | Não executada |
| Falha após commit confirmado | Replay encontra o hash já persistido e retorna `unchanged` | Simulado pelo fake | Não executada |

Não foi possível testar leitura durante atualização, reinício do processo servidor, failover ou commit desconhecido em rede real. Um cliente novo não substitui reinício/failover do Mongo.

## Projeções e RBAC

As projeções de aplicação são explícitas e leem coleções diferentes. Isso evita que o método de leitura pública consulte o documento privado, mas **não é RBAC de MongoDB**: o código não cria roles nem usuários, e uma credencial Mongo com privilégios amplos pode ler diretamente a coleção privada. A futura homologação precisa usar credenciais distintas e provar a negação no servidor.

## Ambiente desta execução

Docker CLI/Compose existiam, mas o Engine não estava disponível. O serviço Docker não pôde ser iniciado sem privilégio. `mongod` não estava disponível. Um serviço MongoDB preexistente permaneceu intocado. Nenhuma consulta, índice ou escrita Mongo ocorreu.
