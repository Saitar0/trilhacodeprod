---
arquivo_id: "f5-18-3-02-eventos-ordem-e-retomada-03-gabarito-quiz"
parent_key: "18.3"
tipo_arquivo: "answer_key"
assunto: "02_eventos_ordem_e_retomada"
ordem: 2
itens_origem: ["Q2"]
---

**Resposta:** EventSource tenta reconectar e pode enviar Last-Event-ID; reconexão e retomada em WebSocket precisam ser implementadas pela aplicação.  
   **Feedback:** até no SSE, o servidor precisa reter eventos e implementar a busca a partir do ID para que haja replay real.

