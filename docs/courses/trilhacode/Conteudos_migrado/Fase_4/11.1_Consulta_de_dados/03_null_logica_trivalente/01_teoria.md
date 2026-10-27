---
arquivo_id: "f4-11-1-03-null-logica-trivalente-01-teoria"
parent_key: "11.1"
tipo_arquivo: "theory"
assunto: "03_null_logica_trivalente"
ordem: 3
itens_origem: ["3. Trate NULL como ausência de valor conhecido"]
---

### 3. Trate NULL como ausência de valor conhecido
NULL não significa zero, string vazia ou falso. Uma comparação comum com NULL, como `status = NULL), resulta em desconhecido em vez de verdadeiro ou falso; por isso, a linha não passa no WHERE. Use `IS NULL) e `IS NOT NULL).

```sql
SELECT id, status
FROM pedido
WHERE status IS NULL;
```

A lógica SQL tem três resultados: verdadeiro, falso e desconhecido. Se qualquer condição necessária do AND for desconhecida, o resultado pode ser desconhecido; WHERE mantém somente o resultado verdadeiro. Com OR, uma condição verdadeira já torna a expressão verdadeira. Aprenda a analisar cada condição antes de combinar filtros.

**Erro comum:** escrever `coluna = NULL) ou comparar NULL com zero para representar ausência.

