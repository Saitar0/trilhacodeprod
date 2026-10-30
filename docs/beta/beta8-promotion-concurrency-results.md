# Beta 8 — Promoção sintética: concorrência, replay e recuperação

## Estado da execução

Executado no MongoDB 7.0.43 em replica set `rsB8`, com um banco aleatório identificado por marcador de propriedade. Uma rede Docker `internal`, sem portas publicadas e sem volume persistente isolou Mongo e harness. O host validou container/image ID, labels, tmpfs, mounts, rede, ausência de port bindings e ausência de volumes antes da primeira conexão/escrita.

## Cenários persistentes

| Cenário | Resultado |
|---|---|
| Lote sintético válido, autorização `content.publish`, revisão/fence atual | Criou documento de geração imutável, atualizou head experimental, gravou auditoria e recibo C8/C10 |
| Mesmo operation ID + mesmo payload | Reaproveitou recibo; não duplicou geração/head/auditoria |
| Mesmo operation ID + hash diferente | Conflito de revisão/idempotência; sem segunda geração |
| Duas promoções da mesma revisão/head | Uma confirmou e a concorrente recebeu `RevisionConflict`; head aponta para um vencedor |
| Ator sem grant | Negado antes da preparação; registrou diagnóstico seguro |
| Operação com grant revogado após autorização de requisição e antes da transação | Participante C12 rejeitou; revisão/head não avançaram |
| Writer com fence obsoleto | `FencingRejected`; efeito de bloco não foi aplicado |
| Coleções operacionais de publicação/trilha | Permaneceram ausentes no banco sintético |
| Encerramento | Marcador foi revalidado; banco, container, rede, imagem de harness e chave temporária foram removidos |

## Limitações

O contrato aceita apenas uma fixture com IDs/namespace/approval explicitamente Beta 8 e não consome o staging Beta 5 nem a primeira fase real. “Promoção” significa criação de geração em coleções `_beta8_experimental_*`; não é publicação. Foram exercitados retries e uma disputa concorrente de head/CAS; falhas naturais de processo entre todos os passos não foram ensaiadas. Não se afirma recovery de produção ou atomicidade fora da transação MongoDB sintética.
