---
arquivo_id: "f4-11-3-04-confirmacao-reversao-dml-01-teoria"
parent_key: "11.3"
tipo_arquivo: "theory"
assunto: "04_confirmacao_reversao_dml"
ordem: 4
itens_origem: ["4. Use transações para operações que precisam ficar juntas"]
---

### 4. Use transações para operações que precisam ficar juntas
Uma transação agrupa operações para que o conjunto seja confirmado com COMMIT ou desfeito com ROLLBACK. Isso é útil para ensaiar uma alteração e verificar seu efeito antes de mantê-la.

```sql
BEGIN;

UPDATE pedido
SET status = 'pago'
WHERE id = 42
RETURNING id, status;

-- Confira o resultado antes de confirmar.
ROLLBACK;
```

Após ROLLBACK, a alteração dessa transação não fica persistida. Se o resultado estiver correto e a operação for intencional, COMMIT confirma. Em psql, um erro pode deixar a transação atual em estado abortado até executar ROLLBACK. Transação não substitui backup, nem protege uma operação executada no banco errado.

**Checklist antes de uma escrita:**
- A conexão aponta para o host e o banco de estudo corretos?
- Você executou o filtro como SELECT e conferiu as linhas?
- O WHERE identifica o alvo que deseja alterar?
- RETURNING ou uma consulta posterior permite confirmar o resultado?
- A operação pode ser ensaiada numa transação e revertida?

