# Beta 8 — Prova de enforcement editorial

## Operação escolhida

Uma atualização sintética de `title`/`body` em um documento cujo `editorial_state` é `draft`. O serviço Beta 8 resolve a trilha a partir do documento, aceita somente os campos e limites definidos no patch, pede `block.update` à autoridade C12 e prepara a operação na autoridade C8/C10. O participante executa o update condicional e insere evento de auditoria na mesma transação do CAS, fence, histórico e recibo.

## Privilégios exercitados

O MongoDB 7 descartável recebeu usuários/roles de escopo por coleção:

* `beta8-runtime`: `find` nos dados sintéticos de conteúdo/geração; update de bloco e insert de publicação foram negados pelo MongoDB.
* `beta8-preparer`: find/insert/update apenas nas coleções sintéticas de staging; update de bloco e insert em head experimental foram negados pelo MongoDB.
* `beta8-editorial-authority`: privilégios necessários às coleções C8/C10/C12 e à mutação experimental; sem privilégios em `tracks`, `track_publications` ou `activity_publications`.

Os erros foram retornados pelo servidor MongoDB como autorização negada, não por validação Python. As provas positivas confirmaram edição autorizada, replay idempotente, auditoria, conflito CAS, fence obsoleto, revogação entre autorização e transação e preservação de dados de aprendizagem ausentes.

## Fronteira de confiança residual

O role `beta8-editorial-authority` precisa de `update` em `content_blocks` e nos registros C8/C12. MongoDB não limita esse privilégio a uma função, revisão, `_id` ou protocolo. Código/processo que possua a credencial da autoridade ainda pode fazer escrita direta. A Beta 8 contém o runtime comum e o preparador, e prova um caminho de mutação controlado, mas não contém globalmente todos os writers nem um processo de autoridade isolado do código chamador.

Nenhuma rota/startup/importador operacional foi conectado. A operação testada altera apenas o bloco sintético de `draft`; não há conteúdo real nem publicação.
