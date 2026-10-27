---
arquivo_id: "f5-18-3-01-transportes-de-tempo-real-01-teoria"
parent_key: "18.3"
tipo_arquivo: "theory"
assunto: "01_transportes_de_tempo_real"
ordem: 1
itens_origem: ["theory-container", "1. Escolher o transporte pela interação"]
---

## Teoria

### 1. Escolher o transporte pela interação
No polling, o cliente faz requisições em intervalos; é simples de operar, mas gera consultas quando não há mudanças e a latência depende do intervalo. No long polling, o servidor mantém uma requisição aberta até haver mudança ou timeout, e o cliente a reabre. SSE mantém uma conexão HTTP para o servidor transmitir eventos ao cliente; é unidirecional, e o cliente envia comandos por requisições HTTP separadas. WebSocket fornece um canal persistente bidirecional, útil quando cliente e servidor precisam trocar mensagens com frequência.

Escolha a partir da direção do fluxo, frequência, latência tolerada, volume, suporte da infraestrutura e complexidade de operação. “Tempo real” não significa latência zero. SSE pode ser a solução menor para notificações somente servidor→cliente; WebSocket não é requisito apenas por haver uma interface dinâmica. [HTML Standard — Server-Sent Events](https://html.spec.whatwg.org/multipage/server-sent-events.html) e [MDN — WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API).

