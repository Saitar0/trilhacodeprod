---
arquivo_id: "f9-44-1-02-injecao-dependencia-persistencia-f02-flashcards"
parent_key: "44.1"
tipo_arquivo: "flashcards"
assunto: "02_injecao_dependencia_persistencia"
ordem: 2
itens_origem: ["FC02", "FC03"]
---


- **Dapper elimina SQL?** Não. SQL explícito faz parte do uso; parâmetros devem representar dados de entrada.
- **Um singleton pode depender diretamente de serviço scoped, como DbContext?** Em geral não. Isso captura uma dependência de escopo curto em objeto compartilhado; crie/consuma escopo corretamente.

