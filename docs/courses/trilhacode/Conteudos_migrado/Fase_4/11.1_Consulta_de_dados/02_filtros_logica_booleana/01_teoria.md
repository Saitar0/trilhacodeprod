---
arquivo_id: "f4-11-1-02-filtros-logica-booleana-01-teoria"
parent_key: "11.1"
tipo_arquivo: "theory"
assunto: "02_filtros_logica_booleana"
ordem: 2
itens_origem: ["2. Filtre linhas com WHERE"]
---

### 2. Filtre linhas com WHERE
WHERE mantém apenas linhas cuja condição resulta em verdadeiro. Comparações como `=), `<>), `>), `>=), `BETWEEN) e `IN) expressam critérios. AND exige que ambas as condições sejam verdadeiras; OR exige pelo menos uma. Use parênteses para tornar explícita a combinação quando houver mistura de AND e OR.

```sql
SELECT id, total, status
FROM pedido
WHERE status = 'pago'
  AND total >= 50;
```

Esse exemplo seleciona pedidos pagos cujo total é pelo menos 50. Texto usa aspas simples; identificadores normalmente não precisam de aspas duplas quando seguem convenções simples do PostgreSQL. Use valores monetários com tipos numéricos apropriados no banco, não com aproximação binária de ponto flutuante.

**Erro comum:** omitir parênteses em uma condição mista e obter resultado diferente do pretendido por causa da precedência dos operadores.

