---
arquivo_id: "f4-16-1-01-modelos-chave-valor-documentos-02-flashcards"
parent_key: "16.1"
tipo_arquivo: "flashcards"
assunto: "01_modelos_chave_valor_documentos"
ordem: 1
itens_origem: ["F1", "F2"]
---

## Flashcards
- **Pergunta:** O que deve orientar as chaves de uma tabela DynamoDB? **Resposta:** os padrões de acesso que a aplicação precisa atender. **Feedback:** a chave de partição é central para localizar e distribuir itens; a chave de ordenação dá suporte à organização e às consultas de itens relacionados.
- **Pergunta:** Por que uma consulta no Firestore pode pedir a criação de um índice? **Resposta:** porque a combinação de filtros e ordenações pode exigir um índice composto que não foi criado automaticamente. **Feedback:** teste as consultas importantes e mantenha os índices necessários junto da configuração do projeto.
