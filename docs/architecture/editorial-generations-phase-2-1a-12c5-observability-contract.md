# Fase 2.1A.12C.5 — Contrato de observabilidade editorial passiva

## Objetivo e fronteira

O módulo [`editorial_observability.py`](../../backend/curriculum_contract/editorial_observability.py) define eventos tipados e um wrapper isolado para observação futura de operações editoriais. Ele não importa FastAPI, serviços, rotas, banco ou adaptador MongoDB; não é importado pelos writers existentes, não registra hooks e não modifica o `__init__.py` do pacote. O valor padrão retornado por `default_instrumentor()` é `NullEditorialInstrumentor`, que apenas chama o callable fornecido.

Este componente é observabilidade, não enforcement: não prova CAS, fencing, persistência, autorização, atomicidade ou completude do inventário. Nenhuma conexão real foi adicionada.

## Evento e privacidade

`EditorialObservationEvent` é um dataclass imutável, com `slots`, schema versão 1 e exatamente estes campos:

| Campo | Tipo fechado | Semântica |
|---|---|---|
| `schema_version` | inteiro fixo `1` | Versão do schema de evento. |
| `operation_kind` | `OperationKind` | ID estático do catálogo. |
| `entrypoint_kind` | `EntryPointKind` | Família de entrada permitida para a operação. |
| `writer_category` | `WriterCategory` | Categoria derivada/verificada contra o catálogo. |
| `outcome` | `OperationOutcome` | Resultado observado ou `unknown`. |
| `duration_bucket` | `DurationBucket` | Bucket, sem duração bruta ou timestamp. |
| `protocol_path` | `ProtocolPath` | Caminho declarado; não prova proteção aplicada. |
| `event_kind` | `EventKind` | `operation_result_observed`; indica apenas emissão da observação. |

Não há campo de extensão. Campos desconhecidos falham na construção; enums aceitam apenas membros já definidos, e valores string livres são recusados pelo schema. `to_public_mapping()` serializa manualmente apenas os oito campos aprovados. Nenhum payload, hash, ID de trilha/nó/aluno/usuário/documento, resposta, título, exceção, mensagem, stack, IP, URI, token, cookie, query string, nome de arquivo ou contexto HTTP é capturado. O módulo não tenta sanitizar um dicionário arbitrário: esses dados não fazem parte do contrato.

O catálogo usa IDs fechados derivados dos grupos W-01–W-13 do [inventário da Fase 12C.4](editorial-generations-phase-2-1a-12c4-writer-inventory.md). Abrange track/node CRUD, ordenação, duplicação, exclusão, publicação, blocos (incluindo quiz blocks sem inventar publicação independente), relações, taxonomias, import, restore, snapshots, integridade, comandos administrativos/seed/migrações, preparação privada e PoC de teste. `OPERATION_CATALOG` é uma visão somente leitura; cada descriptor inclui origem e descrição estáticas, nunca copiadas ao evento. A PoC tem entrypoint exclusivamente `test`.

IDs estáveis da enum `OperationKind`: `track.mutate`, `track.reorder`, `track.duplicate`, `track.delete`, `track.publish`, `node.mutate`, `node.reorder`, `node.duplicate`, `node.delete`, `block.mutate`, `block.reorder`, `relation.mutate`, `taxonomy.mutate`, `import.apply`, `restore.apply`, `snapshot.capture`, `integrity.reconcile`, `admin.ensure_indexes`, `admin.seed`, `admin.legacy_snapshot_migration`, `admin.block_type_migration`, `publication.private_prepare` e `experimental.generation_poc`. Categorias e entrypoints permitidos de cada ID estão no catálogo em código; testes bloqueiam enum ou combinação incompatível.

O catálogo descreve grupos observados no repositório. Ele não prova execução no runtime, não transforma operações históricas/potenciais em writers ativos e não contém descoberta dinâmica de rotas ou funções.

## Contexto e caminhos observados

`ObservationContext` exige um descriptor que seja exatamente o objeto catalogado, um entrypoint permitido e um `ProtocolPath` fechado. Categorias inconsistentes são rejeitadas. Os caminhos `legacy_direct`, `legacy_service`, `revision_protocol` e `unknown` são apenas valores declarativos: um evento que declare `revision_protocol` não comprova CAS ou fencing.

## Resultados

| Resultado | Regra |
|---|---|
| `success` | Só pode ser fornecido explicitamente pelo classificador tipado do chamador. Não é inferido do retorno sem exceção e não comprova commit durável. |
| `conflict` / `rejected` | Exigem classificação explícita, por exemplo a partir de resultado tipado conhecido. |
| `failed` | Resultado padrão quando o callable lança `Exception`; não informa se houve escrita parcial ou commit ambíguo. |
| `cancelled` | Emitido para `asyncio.CancelledError` no wrapper async; não significa rollback nem ausência de commit. |
| `unknown` | Padrão para retorno sem classificador, classificador inválido/falho ou classificação que não possa ser validada. |

O classificador não deve serializar nem mutar seu resultado/exceção; deve retornar somente membro de `OperationOutcome`. Exceções são encaminhadas sem mensagem ou tipo no evento. Para exceções, o classificador é limitado a `conflict`, `rejected`, `failed` ou `unknown`; não pode afirmar `success` nem converter cancelamento em outro resultado.

## Duração

A medição local usa relógio monotônico injetável e não registra timestamp ou duração precisa. Buckets: `<10 ms`; `10 ms–<100 ms`; `100 ms–<1 s`; `1 s–<10 s`; `>=10 s`; `unknown` se leitura falhar, regredir ou produzir valor inválido. O tempo cobre a chamada observada, não o envio do evento.

## Instrumentadores

### Nulo e padrão desabilitado

`NullEditorialInstrumentor` executa o callable uma vez, devolve o mesmo objeto de retorno e propaga a mesma exceção. Não valida nem serializa contexto, emite evento, lê configuração, environment ou `.env`, escreve arquivo, cria thread/tarefa, abre conexão ou inicializa logging. `default_instrumentor()` retorna a instância nula.

### Passivo

`PassiveEditorialInstrumentor.observe_sync(context, callable, ...)` e `observe_async(...)` recebem um callable sem argumentos; os argumentos, se houver, ficam sob controle do chamador e nunca são inspecionados. Executam o callable uma vez, não repetem, não abrem transações, não compensam/rollback, não modificam seus argumentos/retorno e não impõem timeout. Valor e identidade do retorno são preservados. Exceções síncronas mantêm identidade via `raise`; cancelamento async é observado como `cancelled` e relançado.

Falhas comuns (`Exception`) de relógio, classificador ou sink são tratadas fail-open e não substituem o resultado editorial; não há logging do erro. O wrapper não intercepta `BaseException` do callable, preservando sinais de processo e cancelamento fora da exceção async tratada explicitamente. A interface do sink exige `try_emit` não bloqueante; sinks externos não são fornecidos nesta fase. O coletor incluso respeita essa regra. Uma implementação futura de sink deve demonstrar que não bloqueia nem executa I/O externo em linha.

Fail-open pode perder eventos. Logo, esta camada não é auditoria durável nem base de autorização, reconciliação ou garantia de segurança.

## Limites explícitos

1. Instrumentação passiva não impede bypasses.
2. Eventos não demonstram CAS nem fencing efetivamente aplicados.
3. Ausência de eventos não prova ausência de writers.
4. Writers externos ou não versionados permanecem desconhecidos.
5. Coleta fail-open pode descartar eventos.
6. Coletor em memória não é auditoria durável.
7. Não há integração operacional nesta fase.
8. ADR-008 segue bloqueado; esta implementação não promove gates.

## Coletor de teste

`InMemoryEventCollector` é local ao processo, limitado por capacidade (padrão 256), guarda somente eventos validados, descarta novo evento quando cheio ou quando o lock não pode ser obtido imediatamente e não inicia tarefas. `snapshot()`, `dropped_count` e `clear()` apoiam assertions. A leitura/limpeza são operações de teste e podem esperar o lock; a emissão nunca espera. O coletor não é uma implementação de produção e não possui persistência/exportação.

## Integração futura — não realizada

Uma futura chamada deverá construir `ObservationContext` estático em ponto aprovado e envolver a operação correspondente sem capturar request, domínio ou payload. Classificadores deverão mapear somente resultados/tipos explícitos; sucesso precisa de sinal definido pelo contrato da operação. Antes de instrumentar rotas, serviços, jobs, importadores, restauradores, publicadores e CLI, continuam necessários baseline operacional (ADR-008), autorização própria, política de privacidade/retention da telemetria, cobertura completa de writers e testes de transparência. Não adicionar middleware global nem hooks automáticos. A instrumentação isolada desta fase não fecha os bypasses da Fase 12C.4.

## Evidências de teste desta fase

A suíte dedicada contém 36 testes para import sem efeitos colaterais, schema/privacidade, catálogo, resultados, sync/async, identidade de retorno/exceção, cancelamento, falha/contenda/capacidade do sink, duração, concorrência, rede e execução única. O relatório final registra comandos e limitações, incluindo dependência ausente ao tentar executar um teste offline adjacente do adaptador C2.
