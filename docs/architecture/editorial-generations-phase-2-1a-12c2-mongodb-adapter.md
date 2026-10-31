# Fase 2.1A.12C.2 — Adaptador persistente de revisão editorial

## Resultado e limite

Foi implementado um adaptador MongoDB isolado que usa o contrato da Fase 12C.1. O módulo exige um objeto Database explicitamente fornecido, recusa nomes de banco fora de editorial_revision_test_* e não cria cliente nem executa I/O ao ser importado ou construído.

A topologia é verificada por chamada explícita a verify_transaction_topology(). Essa chamada é o primeiro ponto que pode conectar ao servidor e só habilita operações posteriores se a versão for MongoDB 7, houver replica set e sessões lógicas. Nenhum banco foi conectado nesta fase: o daemon Docker local não estava disponível, não havia executável mongod e não foi fornecido URI de teste.

**A estratégia de transação está implementada, mas não está validada em MongoDB.** Portanto, não há evidência de CAS persistente, fencing distribuído, durabilidade ou recuperação após reinício. G2 continua NOT_VERIFIED; G1 continua PARTIAL; G9 e G10 continuam BLOCKED.

## Módulos

- [Adaptador](../../backend/curriculum_contract/mongodb_editorial_revision_adapter.py)
- [Testes de contrato offline](../../backend/unit_tests/test_mongodb_editorial_revision_adapter.py)
- [Suíte de integração MongoDB](../../backend/integration_tests/test_mongodb_editorial_revision_integration.py)
- [Modelo de referência 12C.1](../../backend/curriculum_contract/editorial_revision_protocol.py)
- [Relatório desta fase](./editorial-generations-phase-2-1a-12c2-final-report.md)

O adaptador não é importado por rotas, serviços, leitores, publicadores ou writers ativos. Não implementa publicação de geração nem CAS do head público.

## Contrato e estados

A interface reaproveita os tipos da 12C.1: WriterCredential, FenceAuthorityCredential, PreparedRevision, RevisionReceipt, RevisionRecord e os erros de domínio. MongoDBEditorialRevisionAdapter implementa preparação, confirmação, avanço de fence, abandono, leitura de revisão, histórico e inspeção do estado da operação.

Fluxo conceitual:

1. Inicializar explicitamente uma trilha sintética, com revisão e epoch zero.
2. Provisionar capabilities sintéticas de writer e autoridade de fence. Isso é fixture de teste, não IAM.
3. Avançar o fence por autoridade confiável; a aplicação nunca escolhe a revisão confirmada.
4. Preparar uma operação com identidade estável, revisão-base, epoch e payload JSON validado. A preparação persiste como PREPARED, sem mudar a revisão confirmada.
5. Confirmar por transação. Uma base obsoleta torna a operação CONFLICTED e preserva o payload para recuperação. Fencing obsoleto é rejeitado separadamente.
6. Repetir uma operação idêntica recupera o recibo; identidade reutilizada com writer, base ou payload divergente gera IdempotencyConflict.

O fingerprint mantém o contrato 12C.1: trilha, writer, identidade da operação, revisão esperada e SHA-256 do payload canônico. O fence não faz parte da identidade lógica; uma operação preparada ainda pendente pode ser retomada com o epoch corrente, mas handles antigos deixam de ser válidos.

## Modelo persistente e índices

Todos os nomes são prefixados por um namespace validado e ficam no banco sintético dedicado:

| Coleção | Conteúdo | Restrição |
|---|---|---|
| <ns>_tracks | Revisão atual, epoch de fencing, sequência de controle e última sequência de fence | _id nativo identifica uma trilha |
| <ns>_operations | Intenção preparada, fingerprint, payload canônico, estado e recibo | Índice único (track_id, operation_id) |
| <ns>_history | Registro imutável de cada revisão confirmada | Índice único (track_id, revision) |
| <ns>_writers | Digest de capability sintética e sequência de uso | Índice único (track_id, writer_id) |
| <ns>_authorities | Digest de capability sintética de fence | Índice único (track_id, authority_id) |

Não há TTL, garbage collection ou método para apagar histórico. ensure_indexes() é explícito e só funciona depois de a topologia ter sido verificada. O banco deve ser exclusivamente descartável; a suíte cria um nome aleatório por teste e só o remove se confirmar o marcador de propriedade criado pelo próprio teste.

## Atomicidade, CAS e fencing — desenho implementado, ainda não comprovado no servidor

A confirmação usa ClientSession.with_transaction() com:

- read concern snapshot;
- write concern majority e journal habilitado;
- leitura primária.

Na callback da transação, o adaptador valida a capability do writer, lê estado da trilha, confere fencing_epoch e expected_revision, atualiza condicionalmente o documento de estado, acrescenta histórico e grava o recibo na operação. Uma falha antes do commit da transação deve abortar essas alterações em conjunto.

**Ponto de linearização pretendido:** o commit confirmado da transação MongoDB. O update condicional do documento da trilha serializa revisões concorrentes. O avanço de fencing é um update atômico desse mesmo documento. Ambos incrementam control_sequence; a transação de revisão grava a sequência observada no histórico, e o avanço do fence grava last_fence_sequence. Assim, uma confirmação que disputa com o avanço precisa ser ordenada antes dele ou ser rejeitada no retry da transação. Esse raciocínio ainda precisa de execução contra MongoDB 7 replica set descartável.

A credencial do writer é conferida dentro da transação e seu documento recebe incremento de use_sequence, para serializar uma revogação concorrente com a confirmação. Esse mecanismo é deliberativo e local ao adaptador; não substitui roles MongoDB nem autorização da aplicação.

## Durabilidade e resultado ambíguo

O driver pymongo==4.18.2 usa a API transacional do PyMongo. Em erro rotulado UnknownTransactionCommitResult, o adaptador consulta a operação por identidade:

- COMMITTED: recupera o recibo;
- CONFLICTED: retorna o conflito persistido;
- ABORTED: retorna operação abandonada;
- estado ausente, PREPARED ou consulta indisponível: lança CommitOutcomeUnknown.

Erros sem o label de resultado incerto não são convertidos em sucesso ou conflito; são propagados. A suíte distingue a simulação “commit retornou e o chamador descartou a resposta” de falha real de rede/servidor. Esta última não foi injetada.

Write concern majority com journal é a política configurada; não prova resistência a perda do host, failover de cluster ou topologia de produção. O requisito de transação exclui standalone. Um replica set descartável de nó único, quando disponível, também não provaria failover real.

## Validação de entradas

O contrato limita identidades a 256 bytes UTF-8, segredo sintético a 512 bytes, payload padrão a 4 MiB (configurável até 8 MiB), profundidade JSON a 64 e quantidade de valores a 100.000. Payloads devem ser objetos JSON canônicos, sem valores não finitos, chaves inválidas ou ciclos/valores não serializáveis. Revisão, epoch e sequência persistida respeitam o limite int64 do BSON.

A canonicalização e as validações estruturais ocorrem antes de leituras ou escritas de dados. O limite inferior ao máximo BSON deixa espaço para metadados do documento. A adequação desses limites a conteúdo editorial real continua pendente e não foi inferida a partir de payloads curriculares.

## Evidências realmente obtidas

No ambiente disponível, pymongo==4.18.2 e dnspython==2.9.0 foram instalados somente no .venv da worktree, usando o requisito já fixado pelo projeto para PyMongo. Nenhuma dependência global ou arquivo de requisitos foi alterado.

| Grupo | Resultado | Alcance |
|---|---:|---|
| Regressão 12C.1 em memória | 18/18 aprovados | Modelo RLock de um processo |
| Contratos offline do adaptador | 8/8 aprovados | Guardas sem I/O, canonicalização, identidade, limites e fingerprint |
| Segurança sintática da URI de teste | 3/3 aprovados | Recusa URI remota, credencial, SRV e banco fora do namespace |
| Testes unitários da PoC editorial | 26/26 aprovados | Fakes; sem servidor MongoDB |
| Integração MongoDB | 24 ignorados | URI local descartável ausente; nenhum teste tentou conectar |
| Ruff nos três arquivos Python novos | Aprovado | Sem avisos |
| mypy no adaptador | Aprovado | Sem avisos |
| Multiprocesso | Não executado | Pertence à suíte MongoDB ignorada |
| Transações, rollback e resposta incerta no servidor | Não executados | Sem MongoDB 7 descartável |

Os resultados offline não validam operações MongoDB, atomicidade transacional ou durabilidade.

## Próximos requisitos antes de qualquer reivindicação de G2

1. Disponibilizar um MongoDB 7 em replica set exclusivamente descartável, identificado por URI local sem credenciais.
2. Executar backend.integration_tests.test_mongodb_editorial_revision_integration em base limpa e repetir a suíte integral.
3. Examinar resultados reais de concorrência multiprocesso, T17 (abort transacional), T22 (corrida entre fence e commit) e recuperação por recibo.
4. Registrar versão, topologia, concerns e logs sanitizados.
5. Revisar o adaptador à luz desses resultados.
6. Continuar sem integração ativa: writers reais, grants reais, baseline (G10) e retenção (G9) permanecem fora desta fase.

O adaptador é uma referência isolada e ainda não está pronto para uso em produção.
