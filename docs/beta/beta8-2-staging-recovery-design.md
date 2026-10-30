# Beta 8.2 — recuperação e concorrência do staging

## Caminho exercitado

O teste reutiliza `CurriculumStagingService` Beta 5, `Beta8_1StagingAuthorityBridge` e `Beta8ExperimentalPromoter`. O lote sintético é preparado no namespace Beta 5; o bridge lê estado e checkpoint persistidos, confere contagem/hash/estado `PREPARED`, valida a intenção vinculada ao pacote e entrega o candidato ao grant C12 e ao CAS/fencing C8. A confirmação ocorre em coleções `_beta8_experimental_*`, separadas das coleções operacionais de publicação.

Não há transação única entre as coleções de staging Beta 5 e o commit editorial C8. A garantia é uma sequência recuperável: staging pode ser reexecutado pelo checkpoint; o commit C8 tem identidade de operação e replay; divergências são rejeitadas. Não afirmar atomicidade distribuída.

## Evidências persistentes no MongoDB descartável

| Cenário | Resultado observado |
|---|---|
| Preparação normal e promoção sintética | Lote `PREPARED`; geração e auditoria persistidas. |
| Mesmo comando após sucesso | Mesmo recibo C8 com `replayed=true`; sem geração/auditoria duplicada. |
| Falha injetada após gravar documento e antes do checkpoint | Staging deixou estado `RECOVERABLE`; um registro persistido e zero checkpoints. A repetição pelo serviço Beta 5 completou o lote e o bridge confirmou a geração. |
| Commit persistido e resposta artificialmente perdida | Hook lançou exceção depois do commit durável; retry com mesmo operation ID retornou replay; contagem de geração/auditoria permaneceu estável. |
| Duas transições simultâneas para a mesma revisão/head | Barreira liberou ambas; um commit venceu e o outro recebeu conflito; uma geração nova e um evento de auditoria foram confirmados. |
| Grant revogado depois da autorização inicial e antes do commit | Participante transacional rejeitou a mutação; head permaneceu igual e nenhuma geração foi criada. |
| Geração anterior | Continuou presente após recuperação, retry, corrida e revogação. |
| Preparador tentando escrever no namespace de promoção | MongoDB rejeitou a operação. |

Os pontos de falha e a perda de resposta foram **injetados**, não causados por encerramento natural de processo ou falha espontânea de rede. A recuperação após crash real do processo não foi testada. A concorrência usou tarefas simultâneas, barreira compartilhada e transações MongoDB no replica set descartável.

## Invariantes e limites

* A intenção é vinculada ao lote, hash, trilha e revisão esperada.
* Hash, grant, CAS e fence são verificados antes da geração experimental.
* Retry idêntico é idempotente; a identidade da operação não pode ser reutilizada com payload divergente pelo contrato C8.
* O bridge exige pacote e origem sintéticos; não aceita a fonte real revisada.
* A promoção não chama rotas de publicação, não toca `track_publications` e não altera draft/private.
* A rubrica do projeto 3.5 permanece `PROPOSED`; esta prova não a aprovou.
* Estados persistidos de staging e C8 podem divergir temporariamente entre preparação e autoridade; a recuperação é reexecutar staging e consultar recibo/estado da mesma operação, não uma transação global.

Veredito: **RECUPERAÇÃO E CONCORRÊNCIA DO STAGING VALIDADAS NO ESCOPO EXPERIMENTAL**, limitado aos cenários exercitados.
