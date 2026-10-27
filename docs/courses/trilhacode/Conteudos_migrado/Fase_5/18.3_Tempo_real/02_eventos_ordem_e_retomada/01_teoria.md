---
arquivo_id: "f5-18-3-02-eventos-ordem-e-retomada-01-teoria"
parent_key: "18.3"
tipo_arquivo: "theory"
assunto: "02_eventos_ordem_e_retomada"
ordem: 2
itens_origem: ["2. Formato do evento, ordem e retomada"]
---

### 2. Formato do evento, ordem e retomada
Defina um envelope de mensagem com tipo, identificador, recurso/escopo, sequência ou versão e conteúdo validável. O ID pode ajudar a deduplicar mensagens; uma sequência ajuda a perceber lacunas ou mensagens fora de ordem. O consumidor precisa decidir como ignorar repetição, detectar estado antigo e recuperar lacunas a partir de uma leitura autoritativa.

EventSource tenta reconectar automaticamente e pode enviar Last-Event-ID se o servidor atribuiu IDs aos eventos. Isso só permite retomada efetiva se a aplicação guardar eventos pelo período necessário e souber responder a partir do cursor recebido. WebSocket não define sozinho a política de reconexão, replay ou armazenamento; cliente e servidor precisam implementá-la. Em qualquer transporte, não prometa entrega exatamente uma vez: falhas e retries podem produzir duplicatas. A aplicação pode buscar estado atual ou tornar o processamento idempotente.

