---
arquivo_id: "f5-18-1-01-recursos-e-semantica-http-01-teoria"
parent_key: "18.1"
tipo_arquivo: "theory"
assunto: "01_recursos_e_semantica_http"
ordem: 1
itens_origem: ["theory-container", "1. Recursos, URIs e operações", "2. Semântica, repetição e idempotência"]
---

## Teoria

### 1. Recursos, URIs e operações
Uma API RESTful expõe recursos identificáveis por URI e usa a semântica HTTP para operar sobre eles. Prefira nomes de recursos e caminhos previsíveis, como /tarefas e /tarefas/42. Parâmetros de caminho identificam um recurso; query parameters refinam uma busca ou listagem. Evite fazer GET executar uma ação que altera estado: clientes, robôs e caches podem repetir ou antecipar leituras.

Como ponto de partida para CRUD, GET lê, POST cria ou solicita processamento conforme o contrato, PUT substitui a representação do recurso conhecido, PATCH altera parte dela e DELETE solicita remoção. O corpo, os efeitos e a resposta devem ser documentados. Nem toda API precisa expor todo CRUD, e o caminho não deve ser modelado como uma cópia literal de tabelas internas.

### 2. Semântica, repetição e idempotência
Um método seguro tem semântica essencialmente de leitura. Idempotência significa que repetir a mesma requisição tem o mesmo efeito pretendido no servidor que executá-la uma vez. GET é seguro e idempotente; PUT e DELETE são idempotentes segundo HTTP. POST não é idempotente por padrão. A implementação precisa preservar o contrato: por exemplo, DELETE repetido não deve criar novos efeitos inesperados.

Idempotência não significa que a resposta será idêntica em toda repetição, nem que nenhum log será escrito. Ela descreve o efeito pretendido da operação. Para ações que criam cobranças ou pedidos, repetir uma requisição após timeout pode duplicar o efeito; projetar chaves de idempotência e políticas de repetição é um tópico específico posterior. [RFC 9110 — propriedades dos métodos HTTP](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2).

