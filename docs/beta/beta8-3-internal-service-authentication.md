# Beta 8.3 — Autenticação interna e comandos editoriais

## Protocolo

API e autoridade comunicam-se somente pela rede interna Compose. A API envia HMAC-SHA256 cobrindo versão do protocolo, serviço, método, path, timestamp, nonce e SHA-256 do corpo. A autoridade aceita relógio dentro de 60 segundos e grava o nonce numa coleção persistente com unicidade; falha do ledger ou replay é negado. A resposta também é assinada e vinculada ao nonce, status e corpo. Timeout, conexão recusada ou resposta sem assinatura viram resultado indeterminado/503, nunca escrita direta.

O segredo API↔autoridade é sintético e compartilhado por necessidade do HMAC; a autoridade tem também chave separada para o chamador do bridge do stager. A API não recebe a chave do stager.

## Contrato

O contrato Pydantic fechado aceita apenas `block.update`, `block.create`, `node.update` e uma transição sintética de staging. Campos extras, operação desconhecida, seleção de coleção, `$set` do Mongo, ID de criação não derivado da operação, status de publicação e `authorized=true` são rejeitados. A autoridade resolve o track no recurso, consulta usuário/sessão e projeção C12/grant, e reaplica a verificação de sessão, grant, permissão, revisão e estado dentro da transação de commit.

A API extrai ator e sessão do mecanismo FastAPI existente; campos `actor_id`/`role` no corpo não constituem autoridade. A autoridade ainda confia que o processo API, autenticado pela chave interna, encaminha a identidade daquela requisição. Isso não é uma defesa contra comprometimento total do gateway.

## Operações exercitadas

| Operação | Rota existente | Serviço reutilizado | Resultado persistente |
| --- | --- | --- | --- |
| W-07 PUT | `PUT /api/blocks/{id}` | `services.blocks.update_block` | RPC tipado, grant, CAS, fencing e auditoria |
| W-07 POST | `POST /api/blocks` | `services.blocks.create_block` | ID estável derivado da operação; draft-only |
| W-05 PUT | `PUT /api/nodes/{id}` | `services.nodes.update_node` | RPC tipado, grant, CAS, fencing e auditoria |

Retries HTTP usam a idempotency key já aceita pelas rotas. Retry com o mesmo payload reproduz a decisão; mesma chave com payload divergente conflita. Uma resposta RPC perdida é indeterminada e o chamador pode repetir o mesmo comando; não existe fallback privilegiado.

## Limite de transporte

HMAC fornece autenticação/integridade, não confidencialidade. A prova usa HTTP somente em rede Docker interna sem portas publicadas. Um ambiente operacional exigiria decisão de transporte, gestão/rotação de chaves, observabilidade e proteção contra comprometimento do gateway antes de homologação.
