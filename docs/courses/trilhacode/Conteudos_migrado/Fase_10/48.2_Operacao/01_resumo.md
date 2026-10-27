---
arquivo_id: "f10-48-2-sum"
parent_key: "48.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---


## Resumo
- Streaming exibe partes cedo, mas não garante conclusão nem correção.
- SSE é unidirecional; WebSocket é bidirecional. O fluxo precisa de contrato e ciclo de vida explícitos.
- Erro após fragmentos significa saída parcial; cancelamento da tela não prova cancelamento ou ausência de cobrança no provedor.
- Timeout, rate limit, tamanho e concorrência precisam ser controlados no backend.
- Meça primeiro fragmento, conclusão, falhas, cancelamentos e uso, sem registrar conteúdo sensível desnecessário.

