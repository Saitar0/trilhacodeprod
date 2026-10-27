---
arquivo_id: "f4-11-2-02-cardinalidade-agregacoes-01-teoria"
parent_key: "11.2"
tipo_arquivo: "theory"
assunto: "02_cardinalidade_agregacoes"
ordem: 2
itens_origem: ["3. Entenda o efeito da cardinalidade nas agregações", "4. Separe WHERE, GROUP BY e HAVING"]
---

### 3. Entenda o efeito da cardinalidade nas agregações
COUNT, SUM e AVG resumem as linhas que chegam à agregação. Se a tabela principal tem várias linhas relacionadas, um JOIN aumenta a granularidade. Por exemplo, um pedido com três itens aparece três vezes na junção Pedido–ItemPedido. Somar o total do pedido após essa junção pode contar esse total três vezes.

Agregue no nível adequado. Para receita por item, some quantidade × preço unitário vendido. Para total por pedido, agregue os itens por pedido antes de somar os pedidos. Não use SUM(DISTINCT valor) como correção genérica: dois pedidos diferentes podem ter o mesmo valor e ainda assim ambos devem ser contados.

COUNT(*) conta as linhas resultantes; COUNT(coluna) conta apenas valores não nulos nessa coluna. Com LEFT JOIN, `COUNT(*)) conta também a linha preenchida com NULL para um pai sem correspondência; para contar filhos, use uma coluna obrigatória da tabela filha, como `COUNT(p.id)).

**Erro comum:** somar um atributo do lado “um” após juntá-lo a várias linhas do lado “muitos”.

### 4. Separe WHERE, GROUP BY e HAVING
O fluxo mental útil é: FROM/JOIN formam as linhas; WHERE filtra linhas individuais; GROUP BY reúne as linhas que compartilham os valores indicados; agregações calculam resumos; HAVING filtra os grupos. Use WHERE para restringir registros antes de agregar e HAVING para uma condição que depende do agregado.

```sql
SELECT p.cliente_id, SUM(i.quantidade * i.preco_unitario) AS gasto
FROM pedido AS p
JOIN item_pedido AS i ON i.pedido_id = p.id
WHERE p.status = 'pago'
GROUP BY p.cliente_id
HAVING SUM(i.quantidade * i.preco_unitario) >= 500;
```

Cada coluna do SELECT em uma consulta agrupada precisa estar agrupada ou agregada, salvo dependências funcionais que o PostgreSQL reconheça. SUM e AVG ignoram entradas NULL; COUNT(coluna) também ignora NULL, enquanto COUNT(*) conta linhas. Defina o que NULL significa para a métrica e use COALESCE apenas quando substituir ausência por zero fizer sentido para a regra.

**Erro comum:** colocar uma condição como `SUM(total) >= 500) em WHERE, que filtra linhas e não grupos.

