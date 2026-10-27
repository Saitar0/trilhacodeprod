---
arquivo_id: "f9-42-3-03-sync-async-operacao-f03-flashcards"
parent_key: "42.3"
tipo_arquivo: "flashcards"
assunto: "03_sync_async_operacao"
ordem: 3
itens_origem: ["FC03"]
---


- **`async def` no Flask aumenta automaticamente o número de requisições simultâneas por worker?** Não; Flask continua usando o ciclo WSGI que ocupa um worker por requisição; async pode ajudar com I/O concorrente dentro daquele ciclo.

