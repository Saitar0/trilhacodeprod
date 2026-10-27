---
arquivo_id: "f5-17-1-01-runtime-event-loop-workers-03-gabarito-quiz"
parent_key: "17.1"
tipo_arquivo: "answer_key"
assunto: "01_runtime_event_loop_workers"
ordem: 1
itens_origem: ["Q1", "Q2"]
---

**Resposta:** outras tarefas podem progredir enquanto a operação de I/O aguarda, se a API usada for não bloqueante.  
   **Feedback:** isso é concorrência de I/O; não significa que o JavaScript síncrono da rota está executando em paralelo no mesmo thread.

**Resposta:** ela ocupa o thread principal e atrasa callbacks e outras requisições atendidas pelo event loop.  
   **Feedback:** trabalho longo precisa ser medido e, conforme o caso, dividido, otimizado ou transferido para workers.

