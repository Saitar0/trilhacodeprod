---
arquivo_id: "f4-12-3-04-consultas-sem-multiplicacao-01-teoria"
parent_key: "12.3"
tipo_arquivo: "theory"
assunto: "04_consultas_sem_multiplicacao"
ordem: 4
itens_origem: ["5. Consulte sem multiplicar valores"]
---

### 5. Consulte sem multiplicar valores
Relatórios devem declarar o que significa receita: pedidos pagos ou valores capturados? Qual período e moeda? Um JOIN entre Pedido, ItemPedido e TentativaPagamento pode criar combinações de linhas: duas linhas de item e três tentativas podem produzir seis linhas. Somar valor dos itens nesse resultado multiplica o valor por tentativa; somar pagamento pode multiplicá-lo por item.

Agregue cada entidade na granularidade certa antes de juntar resultados, ou use fontes sem multiplicação. Por exemplo, para receita por mês baseada em pedidos marcados como pagos, agregue itens por pedido e depois junte ao pedido:

```sql
WITH total_por_pedido AS (
  SELECT pedido_id,
         SUM(quantidade * preco_unitario) AS total
  FROM item_pedido
  GROUP BY pedido_id
)
SELECT date_trunc('month', p.criado_em) AS mes,
       SUM(t.total) AS receita
FROM pedido AS p
JOIN total_por_pedido AS t ON t.pedido_id = p.id
WHERE p.status = 'pago'
GROUP BY date_trunc('month', p.criado_em)
ORDER BY mes;
```

Se o relatório precisar de valores realmente capturados, agregue as capturas por pedido separadamente e defina tratamento de estornos, taxas, reembolsos e moeda. Valide os totais com casos pequenos conhecidos antes de confiar num painel.

**Erro comum:** usar SUM(DISTINCT ...) como remendo de duplicação; pedidos diferentes podem ter o mesmo valor e ainda precisam ser somados.

**Checklist de revisão do modelo:**
- As regras e estados temporários foram escritos antes do diagrama?
- ItemPedido preserva preço e quantidade na época da venda?
- Chaves refletem se um produto pode se repetir em várias linhas?
- Constraints cobrem invariantes de uma linha e unicidade necessária?
- Estoque e pedido mudam de forma atômica?
- O pagamento externo pode ser repetido ou ficar em resultado desconhecido?
- O relatório define receita, período e moeda sem multiplicar linhas?

