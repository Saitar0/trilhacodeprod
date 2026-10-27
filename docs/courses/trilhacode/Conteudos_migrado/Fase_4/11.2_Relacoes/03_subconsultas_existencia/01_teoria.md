---
arquivo_id: "f4-11-2-03-subconsultas-existencia-01-teoria"
parent_key: "11.2"
tipo_arquivo: "theory"
assunto: "03_subconsultas_existencia"
ordem: 3
itens_origem: ["5. Use subqueries quando expressam melhor a pergunta"]
---

### 5. Use subqueries quando expressam melhor a pergunta
Subquery é uma consulta usada dentro de outra. EXISTS testa se há pelo menos uma linha correspondente e expressa bem perguntas como “quais clientes possuem algum pedido pago?”:

```sql
SELECT c.id, c.nome
FROM cliente AS c
WHERE EXISTS (
  SELECT 1
  FROM pedido AS p
  WHERE p.cliente_id = c.id
    AND p.status = 'pago'
);
```

A consulta interna pode referenciar a linha externa; por isso, é correlacionada. EXISTS não multiplica a linha do cliente quando há vários pedidos correspondentes. Uma junção também pode expressar essa pergunta, mas pode exigir DISTINCT ou agregação para remover repetição; compare pela clareza da semântica e do resultado.

IN testa pertencimento a um conjunto. Cuidado com NOT IN quando a subquery pode produzir NULL: a lógica de três valores pode impedir que linhas sejam retornadas como esperado. Para “não existe correspondência”, NOT EXISTS costuma deixar a intenção mais direta. Subquery não é automaticamente mais lenta nem mais rápida; desempenho depende do plano e dos dados.

**Erro comum:** escolher JOIN ou subquery por uma regra simplista de desempenho sem verificar o significado e o plano da consulta.

