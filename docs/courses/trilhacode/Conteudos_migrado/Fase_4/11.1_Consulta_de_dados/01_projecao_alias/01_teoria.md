---
arquivo_id: "f4-11-1-01-projecao-alias-01-teoria"
parent_key: "11.1"
tipo_arquivo: "theory"
assunto: "01_projecao_alias"
ordem: 1
itens_origem: ["1. Defina a forma do resultado"]
---

## Teoria

### 1. Defina a forma do resultado
Uma consulta SELECT lê dados sem alterar a tabela. FROM indica a tabela ou fonte; a lista após SELECT escolhe as colunas e expressões que aparecem no resultado. Evite `SELECT *) em relatórios e integrações quando o consumidor precisa de um formato previsível: selecionar explicitamente as colunas reduz dados desnecessários e deixa o contrato visível.

Aliases com AS dão nomes claros ao resultado, inclusive para expressões. Por exemplo:

```sql
SELECT id, total AS valor_pedido
FROM pedido;
```

A consulta retorna duas colunas, chamadas id e valor_pedido. O alias não altera o nome persistido na tabela. Sem DISTINCT, linhas repetidas no resultado podem permanecer; selecionar menos colunas pode fazer linhas diferentes parecerem iguais, mas não elimina as linhas.

**Erro comum:** achar que o nome após AS renomeia permanentemente a coluna da tabela ou que SELECT remove duplicatas por padrão.

