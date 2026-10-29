# Fase 2.1A.12C.7 — Atomicidade entre `update_block` e auditoria

## Escopo e classificação das evidências

Esta fase executa o serviço `update_block` e a função `audit` reais a partir dos arquivos versionados, substituindo apenas os módulos de dependência operacional por um proxy para um MongoDB descartável. A solução transacional é um módulo experimental de teste; nenhum writer, rota, serviço ativo, schema operacional ou configuração foi alterado. O ponto de partida é o W-05 e o harness da [Fase 12C.6](editorial-generations-phase-2-1a-12c6-writer-harness.md), com inventário em [12C.4](editorial-generations-phase-2-1a-12c4-writer-inventory.md).

As conclusões distinguem **OBSERVADO_NO_CÓDIGO**, **VERIFICADO_NO_MONGODB_DESCARTÁVEL**, **FALHA_INJETADA_APÓS_CONFIRMAÇÃO** e **NÃO_VERIFICADO**. Uma exceção injetada depois de uma chamada MongoDB confirmada não é apresentada como falha de rede real.

## Caminho real

A rota [`routes_content.py`](../../backend/routes_content.py#L166-L168) exige `content.write`, converte o modelo de entrada e chama o serviço. O serviço [`blocks.py`](../../backend/services/blocks.py#L38-L45) executa:

1. Lê `content_blocks` por `_id` por meio de [`get_document`](../../backend/services/common.py#L24-L28).
2. Valida `status`, acrescenta `updated_at` ao dicionário de entrada e executa `update_one` com filtro somente por `_id`.
3. Aguarda `audit(user, "block", ...)`.
4. Faz uma leitura final do bloco e retorna o resultado.

A função real [`audit.py`](../../backend/audit.py#L7-L11) insere em `edit_history`. Ela não recebe sessão, não recebe `session` da chamada do writer e não usa outbox ou fallback. O writer também não inicia uma transação e ignora `matched_count`. O módulo [`database.py`](../../backend/database.py#L1-L8) cria `AsyncMongoClient` no import; por isso o harness carrega os fontes por execução isolada e nunca importa esse módulo operacional.

**Papel da auditoria:** o fluxo atual aguarda a auditoria e propaga sua exceção, de modo que a chamada não retorna sucesso se a gravação falhar. Isso é comportamento observado. O código não esclarece se a auditoria é uma obrigação de negócio transacional ou uma telemetria cuja falha poderia ser tolerada; a política permanece decisão humana. A observabilidade passiva das fases anteriores não foi tratada como auditoria funcional.

## Ambiente descartável

| Propriedade | Evidência observada |
|---|---|
| MongoDB | `7.0.43`, imagem oficial local `mongo:7.0.43`, image ID `sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b` |
| Topologia | Replica set `rs12c7`, um membro `127.0.0.1:52926`, estado `PRIMARY`; sessões lógicas disponíveis |
| Armazenamento | WiredTiger; `/data/db` e `/data/configdb` em `tmpfs` de 256 MiB e 64 MiB, sem mounts persistentes ou bind mounts |
| Driver | PyMongo Async `4.18.2`, Python `3.11.9`, instalado em venv descartável fora do repositório |
| Contêiner | `a0e3b21133b1cfe446aac90ea019cf58795950b9a44344c37cb1422f5246293b`; label `io.trilhacode.phase=2.1a.12c7` |
| Rede | `trilhacode-12c7-update-block-net`, bridge exclusiva, masquerade de saída desativado; somente o contêiner da fase conectado |
| Porta | Publicada apenas em `127.0.0.1:52926`; a porta 27017, ocupada por processo alheio, não foi usada |
| Banco por teste | `editorial_block_audit_test_<16 hex>`; marcador de propriedade criado antes das fixtures e verificado antes de cada descarte |

Cada execução criou somente documentos sintéticos. Os bancos de teste foram descartados após cada caso; a verificação final não encontrou bancos com esse prefixo. O contêiner usa `--rm`; apenas o contêiner e a rede etiquetados desta fase foram interrompidos/removidos ao final. Os volumes anônimos da tentativa inicial foram removidos junto com o contêiner; inspeção posterior confirmou que já não existem. Os testes conectaram somente ao endereço loopback da fase; nenhum endpoint, banco ou serviço da aplicação, staging ou produção foi acessado. A dependência PyMongo foi instalada em venv temporário, fora do repositório.

O replica set de nó único permite transações, mas `w: "majority"` representa confirmação do único membro disponível. Esses testes não demonstram tolerância a falhas, failover ou durabilidade equivalente a um cluster de produção com múltiplos membros.

## Reprodução do writer atual no MongoDB

O harness [`editorial_block_atomicity_harness.py`](../../backend/integration_tests/editorial_block_atomicity_harness.py) executa o fonte real de `blocks.py`, `audit.py`, `services/common.py`, `serialization.py` e utilitários necessários. A única alteração é o vínculo local de `database.db` com a base descartável, por módulos de import isolados; nenhuma função de escrita foi copiada para substituir o writer.

| Cenário | Execução e estado persistido observado |
|---|---|
| R1 — sucesso normal | `content_blocks` atualizado e um documento em `edit_history`; a função retorna o bloco. |
| R2 — falha antes da atualização | Falha injetada antes do comando; bloco inalterado e sem auditoria. |
| R3 — falha do Mongo durante a atualização | Validador `$jsonSchema` rejeita um campo sintético; MongoDB rejeita atomicamente a atualização do documento e não há auditoria. |
| R4 — erro após confirmação da atualização | Proxy aguarda o `update_one` real completar e então injeta erro; o bloco permanece alterado, sem auditoria. É falha na fronteira do harness após confirmação, não falha de rede. |
| R5 — falha antes do insert de auditoria | O `update_one` real já foi confirmado; o insert não é enviado; bloco alterado, sem auditoria e erro propagado ao chamador. |
| R6 — insert de auditoria confirmado, resposta perdida | O insert real é concluído e o proxy então injeta erro; bloco e auditoria permanecem, mas o chamador recebe erro. |
| R7 — falha da leitura final | A falha ocorre na leitura de retorno, depois das duas escritas; ambas permanecem no banco e a chamada falha. |
| R8 — retry após auditoria não inserida | A primeira chamada altera o bloco e falha na auditoria; a repetição atualiza novamente e grava auditoria. Não existe identidade idempotente no writer. |
| R9 — retry após confirmação da auditoria sem resposta | A primeira chamada altera bloco e grava auditoria, mas o harness injeta erro após o insert; repetir a chamada atual grava uma segunda linha de auditoria. |
| R10 — concorrência do writer atual | Duas chamadas sincronizadas leem a mesma versão-base; ambas atualizam e ambas gravam auditoria. As duas retornam; o título final é o de uma delas, sem garantia de qual. |
| Resposta perdida no chamador | Uma falha sintética é lançada após o writer retornar; bloco e auditoria já estão persistidos. Não foi simulada uma conexão de rede interrompida. |

Esses resultados confirmam que atualização e auditoria são operações independentes. O driver pode tratar retries de comandos individuais segundo as regras de retryable writes, mas a chamada de aplicação não tem uma chave que torne a combinação `update + audit` idempotente. Um retry da requisição inteira pode reaplicar a atualização e duplicar a auditoria. Além disso, `matched_count == 0` não é verificado: a partir do código, é possível seguir para auditoria mesmo se o documento deixar de corresponder ao filtro entre a leitura inicial e a atualização; esse interleaving específico não foi exercitado.

## Proposta transacional experimental

O módulo [`experimental_block_audit_transaction.py`](../../backend/curriculum_contract/experimental_block_audit_transaction.py) é **somente para teste** e não é importado por rotas, serviços ou startup. Ele recusa nomes de banco fora de `editorial_block_audit_test_<16 hex>` e aceita apenas os campos sintéticos `title` e `status`. Ele assume, como hipótese a deliberar, que a auditoria é obrigatória para a confirmação editorial. Ambas as coleções precisam residir no mesmo deployment MongoDB.

A operação experimental usa uma sessão e transação MongoDB com read concern `snapshot`, write concern `majority` com journal e primary read preference. Ela:

1. Lê o bloco na sessão e confere `editorial_revision` esperada.
2. Atualiza com filtro por `_id` e revisão esperada, incrementando a revisão.
3. Insere a auditoria com a mesma sessão, `operation_id` estável e índice único parcial para IDs experimentais.
4. Lê o estado resultante na sessão e só então tenta confirmar a transação.
5. Aborta se uma falha ocorrer antes da confirmação; não repete a mutação automaticamente.

Os testes demonstraram confirmação conjunta, rollback após falha anterior ao insert e após o insert ter sido aplicado dentro da transação mas antes do commit, rejeição de revisão obsoleta e um vencedor em duas transações concorrentes. Repetir a mesma operação não retorna sucesso idempotente: a proposta rejeita a revisão antiga ou a identidade duplicada e não cria uma segunda revisão/auditoria. Resultado de commit com rótulo `UnknownTransactionCommitResult` é convertido em `BlockCommitOutcomeUnknown`, que requer reconciliação. A chamada do driver `commit_transaction()` possui seu próprio retry limitado do comando de commit; o código de domínio não repete a atualização nem o insert. O cenário de resultado desconhecido não foi provocado por falha de rede nesta fase.

O campo `editorial_revision` foi criado exclusivamente em documentos sintéticos; não existe evidência de que o modelo atual tenha esse campo. A proposta experimental não conecta o adaptador de revisão da 12C.2 e não implementa fencing, autoridade de writer, idempotência com replay de recibo, autorização, geração imutável ou CAS do head público. Portanto, não é substituta do protocolo C1/C2, nem prova de compatibilidade com os schemas atuais. Uma auditoria externa ao mesmo MongoDB exigiria outro contrato, como outbox transacional; nenhuma integração externa foi implementada.

## Comparação observada

| Critério | `update_block` atual | Proposta transacional isolada |
|---|---|---|
| Atualização e auditoria confirmadas juntas | Não; chamadas separadas sem sessão explícita | Sim, quando a transação MongoDB conclui com sucesso |
| Falha antes/na auditoria | Atualização anterior permanece | Atualização é abortada junto com auditoria |
| Auditoria inserida e resposta do insert perdida | Bloco e linha de auditoria permanecem; writer retorna erro | Falha antes do commit aborta ambas; commit ambíguo permanece explicitamente indeterminado |
| Concorrência lógica | Sem CAS; duas chamadas concorrentes tiveram sucesso | CAS sintético por revisão: um vencedor observado; conflito transacional não é repetido |
| Retry/idempotência | Retry da chamada pode duplicar auditoria | Chave de operação única evita duplicação, mas replay de recibo não é fornecido |
| Commit desconhecido | Não há tratamento de transação | Tipo explícito previsto; não injetado/testado contra falha de rede |
| Efeitos externos | Audit atual é outra coleção MongoDB via cliente compartilhado | Atomicidade somente se todas as gravações participarem da mesma transação no mesmo deployment |

## Limitações e decisão pendente

- Os testes transacionais foram executados em replica set descartável de nó único, não em staging ou produção.
- As falhas “após confirmação” são injetadas no harness imediatamente depois de uma chamada real ao MongoDB retornar; não são cortes de conexão nem failover.
- A concorrência foi exercitada por tarefas assíncronas com conexões/sessões próprias por transação, não por processos separados.
- Nenhum teste cobre transação em topologia multi-membro, failover, commit ambíguo real, carga, latência operacional ou compatibilidade do driver implantado.
- A política de negócio para obrigatoriedade da auditoria não está especificada no código. Uma decisão humana precisa confirmar essa exigência antes de qualquer integração.
- Transação não substitui CAS de revisão, fencing, idempotência de requisição, proteção contra writers legados, geração imutável ou publicação atômica.
- Os estados dos gates não mudam: G1 `PARTIAL`, G2 `NOT_VERIFIED`, G3 `NOT_VERIFIED`, G4 `PARTIAL`, G5 `NOT_VERIFIED`, G6 `PARTIAL`, G7 `PARTIAL`, G8 `NOT_VERIFIED`, G9 `BLOCKED`, G10 `BLOCKED`.
