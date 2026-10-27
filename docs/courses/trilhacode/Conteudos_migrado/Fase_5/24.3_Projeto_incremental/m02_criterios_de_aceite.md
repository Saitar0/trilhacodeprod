---
arquivo_id: "f5-24-3-m02-criterios-de-aceite"
parent_key: "24.3"
tipo_arquivo: "acceptance_criteria"
ordem: 2
itens_origem: ["M2"]
titulo_marco: "Marco 2 — API autenticada e persistência migrável"
---

**Aceite:** após recriar o banco e aplicar migrations, a rota persiste e recupera o recurso; usuário não autorizado não lê nem modifica o recurso; não é possível selecionar outra identidade enviando `ownerId` livremente no corpo da requisição.

