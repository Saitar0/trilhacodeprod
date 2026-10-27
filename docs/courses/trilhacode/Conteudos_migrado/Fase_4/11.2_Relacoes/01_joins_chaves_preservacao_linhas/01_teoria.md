---
arquivo_id: "f4-11-2-01-joins-chaves-preservacao-linhas-01-teoria"
parent_key: "11.2"
tipo_arquivo: "theory"
assunto: "01_joins_chaves_preservacao_linhas"
ordem: 1
itens_origem: ["1. Relacione linhas pela chave correta", "2. Preserve linhas com LEFT JOIN e posicione condições"]
---

## Teoria

### 1. Relacione linhas pela chave correta
JOIN combina linhas de fontes diferentes segundo uma condição. Em um modelo relacional, a condição costuma ligar a chave primária de uma tabela à chave estrangeira da outra. Use aliases para deixar claro de onde vêm as colunas e qual papel cada tabela ocupa.

```sql
SELECT p.id AS pedido_id, p.criado_em, i.produto_id, i.quantidade
FROM pedido AS p
JOIN item_pedido AS i ON i.pedido_id = p.id;
```

INNER JOIN mantém apenas pares que satisfazem ON. Um pedido sem itens não aparece. A condição deve representar a relação real; ligar tabelas apenas por nomes iguais ou usar uma coluna sem unicidade pode criar associações erradas. JOIN sem condição pode gerar produto cartesiano, combinando cada linha de uma tabela com todas da outra.

Preveja quantas linhas podem sair: um Pedido ligado a seus ItensPedido gera uma linha por item, não necessariamente uma linha por pedido. Antes de agregar, inspecione a granularidade do resultado — o que cada linha representa depois da junção.

**Erro comum:** esperar que uma junção 1:N preserve uma linha por registro do lado 1.

### 2. Preserve linhas com LEFT JOIN e posicione condições
LEFT JOIN mantém todas as linhas da tabela à esquerda. Quando não existe correspondência à direita, as colunas da tabela direita vêm como NULL. Isso é útil para encontrar clientes sem pedidos:

```sql
SELECT c.id, c.nome
FROM cliente AS c
LEFT JOIN pedido AS p ON p.cliente_id = c.id
WHERE p.id IS NULL;
```

A posição da condição importa. Se o objetivo é manter clientes mesmo quando não têm pedido pago, coloque a condição de status no ON:

```sql
SELECT c.id, p.id AS pedido_id
FROM cliente AS c
LEFT JOIN pedido AS p
  ON p.cliente_id = c.id
 AND p.status = 'pago';
```

Colocar `p.status = 'pago') no WHERE elimina as linhas sem pedido, pois o valor NULL não satisfaz a condição. O LEFT JOIN passa a se comportar como uma filtragem de correspondências, o que pode ser o desejado, mas não preserva todos os clientes.

**Erro comum:** mover uma condição da tabela direita de ON para WHERE sem verificar se as linhas sem correspondência ainda devem aparecer.

