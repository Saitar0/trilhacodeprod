# Fase 2.1A.12C.1 — Protocolo isolado de revisão editorial

## 1. Objetivo e limite

Este módulo fornece uma referência executável, independente de FastAPI, para preparação e confirmação de revisões editoriais por trilha. Implementa numeração monotônica atribuída pelo protocolo, CAS, fencing, conflitos explícitos, idempotência e histórico imutável dentro de uma única instância Python.

**Não é adaptador MongoDB nem implementação pronta para produção.** A sincronização usa um `threading.RLock` local ao processo. Nenhuma rota, serviço ativo, publicador, leitor de aluno, coleção real ou feature flag utiliza este componente. Os estados de credenciais também são provisórios e vivem apenas na instância em memória.

Referências de arquitetura: [protocolo de revisão B.6](./editorial-generations-phase-2-1a-12b6-revision-protocol.md), [coexistência dos escritores B.6](./editorial-generations-phase-2-1a-12b6-writer-coexistence.md), [invariantes integrados B.6](./editorial-generations-phase-2-1a-12b6-integrated-invariants.md), [deliberações B.7](./editorial-generations-phase-2-1a-12b7-human-decision-register.md) e [decisões de aprendizagem B.8](./editorial-generations-phase-2-1a-12b8-learning-policy-addendum.md).

## 2. Contratos do módulo

Implementação: `backend/curriculum_contract/editorial_revision_protocol.py`. Exportações: `backend/curriculum_contract/__init__.py`.

| Tipo/operação | Responsabilidade |
|---|---|
| `EditorialRevisionProtocol` | Interface conceitual de domínio com `prepare` e `commit`; uma implementação persistente terá de cumprir a atomicidade exigida no commit. |
| `InMemoryEditorialRevisionProtocol` | Implementação de referência thread-safe, exclusivamente em memória e por processo. |
| `WriterCredential` | Capacidade opaca escopada a `track_id` e `writer_id`, provisionada pela instância de referência. Seu provisionamento não é IAM. |
| `FenceAuthorityCredential` / `advance_fence` | Autoridade escopada que avança o epoch inteiro da trilha. Cada epoch invalida handles preparados com token anterior. |
| `prepare(...)` | Valida identidade, revisão-base, token, payload JSON canônico, fingerprint e validador opcional; cria somente estado `PREPARED`. |
| `commit(prepared, credential)` | Sob a mesma trava, autentica, verifica handle, estado, fence atual e revisão esperada; atribui `current + 1`, acrescenta histórico e guarda recibo. |
| `RevisionReceipt` | Resultado estável: trilha, operação, escritor, revisão, parent, fence, hash e fingerprint; replay informa `replayed=True` sem nova revisão. |
| `RevisionConflict` / `FencingRejected` | Resultados diferentes para base obsoleta e epoch obsoleto. |
| `IdempotencyConflict` / `WriterAuthorizationError` | Identidade reutilizada com outra intenção e credencial ausente, revogada ou fora do escopo. |
| `history`, `read_revision`, `prepared_payload`, `operation_state`, `abandon` | Inspeção/recuperação local de estado de referência, sem contrato HTTP. |

`expected_revision` é a revisão de origem declarada pelo comando. O protocolo não escolhe número de revisão o cliente: a revisão confirmada é calculada como a atual mais um somente no ponto de confirmação. O fingerprint liga trilha, escritor, operação, revisão esperada e SHA-256 do payload canônico; o fencing token não altera a identidade lógica da operação. Um retry pendente pode ser preparado novamente com epoch atual, mas um handle antigo continua rejeitado.

## 3. Revisão, CAS e conflito

Cada trilha inicia na revisão lógica zero. Um commit válido condicionado a `current_revision == expected_revision` acrescenta exatamente um registro com sequência seguinte e parent explícito. Duas propostas distintas sobre a mesma revisão não podem ambas vencer. A perdedora fica `CONFLICTED`; seu payload preparado continua recuperável por `prepared_payload` enquanto a credencial for válida. Não há rebase, merge ou reescrita automática.

O ponto de linearização do modelo é a seção crítica de `commit`: verificação de credencial, handle, operação, fence e CAS, seguida da gravação do recibo e do registro histórico, são executadas sob o mesmo lock. Isso demonstra a propriedade **somente no modelo de processo único**.

## 4. Fencing e autorização

O fence é um epoch monotônico por trilha, emitido pela autoridade de referência. Escritores autorizados podem receber o mesmo epoch dentro de uma época de edição; o CAS resolve concorrência de revisão entre eles. Avançar o epoch invalida todos os handles anteriores, mesmo que nenhuma revisão tenha mudado. Expiração de lease não é implementada; um futuro coordenador deve avançar o fence ao revogar/tomar posse e não distribuir o novo token a um writer removido. Se o writer perder autorização, a credencial também precisa ser revogada. O modelo não implementa associação entre epoch e titular de lease, nem política de renovação. O token não é reutilizado dentro da instância.

Credenciais são capabilities aleatórias guardadas por digest e verificadas com comparação constante. Isso é um mecanismo didático local, não autenticação resistente a comprometimento do processo nem substituto para roles/credenciais MongoDB. O provisionamento de credenciais e autoridade existe para fixtures e não está conectado a usuários.

## 5. Preparação, integridade e idempotência

Payloads aceitam somente valores JSON finitos, com chaves string. A canonicalização determinística calcula hash e congela cópias imutáveis; alteração posterior do objeto original não muda a proposta. Um `proposal_validator` opcional permite rejeitar semanticamente uma proposta antes de registrar a preparação. Rejeição não cria operação nem revisão.

Preparação não confirma revisão. Falha ou abandono antes do commit deixa a revisão corrente e o histórico intactos. Repetição idêntica da mesma operação retorna o resultado original; reuso da chave com escritor, revisão-base ou conteúdo diferente gera conflito. Identidade é escopada por `(track_id, operation_id)`, prevenindo reuso cruzado entre trilhas.

## 6. Falhas exercitadas

Os testes locais cobrem:

- duas propostas/escritores concorrentes com a mesma base: um commit e um conflito;
- revisão obsoleta com draft perdedora recuperável;
- fencing antigo rejeitado depois de novo epoch, tanto antes quanto depois de alteração de conteúdo;
- handle antigo não pode abandonar uma preparação retomada sob fencing novo;
- replays idênticos e reuso divergente de operação, inclusive concorrente;
- resposta perdida simulada após commit e recuperação do recibo;
- preparação não confirmada, abandono e validação de proposta inconsistente;
- credenciais revogadas/forjadas e autoridade de fence não autorizada;
- isolamento entre trilhas, histórico monotônico e oito rodadas concorrentes com seis escritores.

O timeout do teste T9 é simulado no chamador após a confirmação em memória; não representa falha de rede ou crash de processo real. Não foram exercitados crash/power-loss entre gravações, reinício de processo, expiração temporal, consistência entre instâncias, journaling, write concern ou comportamento de servidor MongoDB.

## 7. Matriz de invariantes

| Invariante | Implementado | Testado | Limitação |
|---|---|---|---|
| Revisão monotônica | Sim, contador mantido pela instância | Sim: T1, T13, T15 | Não é contador persistente/distribuído. |
| CAS de revisão | Sim, comparação e append sob lock único | Sim: T2, T3, T15 | Não demonstra CAS atômico em MongoDB ou entre processos. |
| Fencing contra escritor obsoleto | Sim, valida epoch atual no commit e em abandono mutável | Sim: T4, T5, T16 | Avanço é chamada explícita da autoridade; lease real não existe aqui. |
| Conflitos explícitos | Sim: `RevisionConflict`, `FencingRejected`, `IdempotencyConflict` e `WriterAuthorizationError` | Sim: T2–T7, T14 | Mapeamento HTTP futuro não foi implementado. |
| Idempotência | Sim, chave por trilha + fingerprint lógico + recibo | Sim: T6–T9 e concorrência T15 | Livro de recibos só é durável enquanto o processo vive. |
| Isolamento entre trilhas | Sim, estado e operação escopados por trilha | Sim: T12 | Sem autorização multi-tenant real. |
| Preparação distinta de confirmação | Sim, `PREPARED` separado de `COMMITTED` | Sim: T10, T11 | Sem artefatos persistentes externos. |
| Recuperação de commit sem resposta | Sim, replay devolve recibo original | Sim: T9 | Simulado no chamador; sem crash/restart real. |
| Ausência de revisões duplicadas | Sim, incremento sob lock | Sim: T2, T8, T13, T15 | Garantia apenas dentro de uma instância. |
| Compatibilidade com persistência real | Não | Não | Exige adapter e testes em topologia descartável aprovada. |

## 8. Requisitos para persistência futura

Um adapter não poderá decompor o commit em “ler em memória, depois escrever sem condição”. A operação durável deverá coordenar revisão esperada, fencing atual, identidade/fingerprint, recibo e histórico. Se esses elementos ocuparem múltiplos documentos, a arquitetura terá de declarar e validar as garantias/topologia que suportam a atomicidade; não se presume que MongoDB standalone ofereça transação multidocumento. Alternativa de registro em um documento limitado ou protocolo recuperável também exigirá decisão, limite de tamanho, recuperação e testes específicos.

O modelo atual não impõe limite máximo de bytes/profundidade do JSON nem comprimento máximo das identidades; elas só precisam ser strings não vazias. Como o módulo não recebe tráfego de clientes nem é importado por rotas ativas, isso não cria uma exposição atual. Antes de tornar a interface acessível a entradas não confiáveis, limites de recursos e formato/escopo das identidades precisam ser definidos e testados.

Antes de qualquer integração: inventário completo e bloqueio de writers legados (G1), CAS/fence/idempotência demonstrados no storage escolhido (G2), snapshot coerente e cobertura de fontes (G3), revisão de segurança, topologia, write concern, replay durável, observabilidade e autorização independente. O módulo atual não satisfaz G1, não satisfaz G2 integralmente e não desbloqueia G10.

Este módulo não implementa publicação de gerações nem CAS do head público. Esses contratos continuam separados e dependem de snapshot coerente, proteção público/privado e decisão operacional.
