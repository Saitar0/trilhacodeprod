---
arquivo_id: "f5-18-1-01-recursos-e-semantica-http-03-gabarito-quiz"
parent_key: "18.1"
tipo_arquivo: "answer_key"
assunto: "01_recursos_e_semantica_http"
ordem: 1
itens_origem: ["Q1", "Q2"]
---

**Resposta:** GET tem semântica segura de leitura; clientes podem repetir ou antecipar a chamada, então a alteração deve usar uma operação apropriada para mudança de estado.  
   **Feedback:** não use GET para ações mutáveis. A semântica uniforme é necessária para clientes, caches e ferramentas HTTP.

**Resposta:** repetir a mesma requisição deve produzir o mesmo efeito pretendido no servidor que executá-la uma vez.  
   **Feedback:** isso não exige respostas byte a byte idênticas nem impede logs; descreve o efeito da operação.

