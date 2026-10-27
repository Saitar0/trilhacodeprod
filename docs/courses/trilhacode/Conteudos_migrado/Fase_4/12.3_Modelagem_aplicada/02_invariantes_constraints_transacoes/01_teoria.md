---
arquivo_id: "f4-12-3-02-invariantes-constraints-transacoes-01-teoria"
parent_key: "12.3"
tipo_arquivo: "theory"
assunto: "02_invariantes_constraints_transacoes"
ordem: 2
itens_origem: ["3. Expresse invariantes com constraints e transações"]
---

### 3. Expresse invariantes com constraints e transações
Use PK e FK para identidade e referências, NOT NULL para presença obrigatória, UNIQUE para unicidade e CHECK para regras da linha, como quantidade > 0 ou valor não negativo. Para manter histórico, excluir um produto que aparece em um pedido pode ser proibido ou o produto pode ser arquivado; a política deve refletir o ciclo de vida. Uma constraint não garante sozinha regras que dependem de diversas escritas coordenadas.

Estoque pode ser modelado como saldo atual, ledger de movimentos ou uma combinação em que o saldo seja atualizado atomicamente junto ao registro do movimento. Escolha uma fonte de verdade e mantenha qualquer projeção derivada na mesma transação ou com processo de reconciliação definido. Para uma reserva simples, uma atualização condicional é um caminho:

```sql
UPDATE estoque
SET disponivel = disponivel - 1
WHERE produto_id = 42
  AND disponivel >= 1
RETURNING produto_id, disponivel;
```

Execute a atualização e a criação do item/reserva dentro da transação apropriada. Se nenhuma linha retornar, não confirme a venda como se o estoque tivesse sido reservado. Concorrência, cancelamento, expiração da reserva e devolução também precisam de regras explícitas.

**Erro comum:** atualizar estoque e inserir o pedido em operações independentes, permitindo que uma parte seja confirmada sem a outra.

