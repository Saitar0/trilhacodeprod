---
arquivo_id: "f4-12-2-90-integracao-kp01-gabarito-pratica"
parent_key: "12.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_transacoes_isolamento_concorrencia", "02_locks_conflitos_otimistas_pessimistas"]
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:**
```sql
UPDATE produto
SET estoque = estoque - 1
WHERE id = 42
  AND estoque >= 1
RETURNING id, estoque;
```
Uma tentativa retorna a linha e deixa estoque 0; a concorrente não satisfaz mais a condição e não atualiza linhas. Para distinguir inexistência de saldo insuficiente, faça uma consulta específica após a tentativa, lembrando que estado pode mudar novamente; a regra e a resposta da API devem considerar essa concorrência. A implementação ingênua tem uma janela entre leitura e escrita.

