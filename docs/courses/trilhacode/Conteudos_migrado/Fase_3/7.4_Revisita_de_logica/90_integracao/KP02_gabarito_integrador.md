---
arquivo_id: "f3-7-4-90-integracao-kp02-gabarito-integrador"
parent_key: "7.4"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_transformacoes_e_colecoes", "02_complexidade", "03_pilhas_e_filas"]
ordem: 2
itens_origem: ["P2"]
---

<details>
<summary>Gabarito comentado — abra somente após tentar</summary>

1. A seleção contém pedidos 1 e 3. As linhas são `{ id: 1, cliente: "Lia", total: 30 }` e `{ id: 3, cliente: "Lia", total: 8 }`.
2. Um acumulador por cliente pode começar como `{}`; para cada pedido concluído, somar o total à chave existente ou iniciar essa chave em zero. Resultado: `{ Lia: 38 }`. Uma implementação equivalente é `reduce((acumulado, pedido) => { acumulado[pedido.cliente] = (acumulado[pedido.cliente] ?? 0) + pedido.total; return acumulado; }, {})` sobre a lista filtrada.
3. Três passagens sequenciais completas têm custo proporcional a `3n`, portanto continuam `O(n)`; uma passagem integrada também é `O(n)`. A passagem única pode reduzir percursos, mas costuma concentrar mais lógica e exige atenção para preservar legibilidade. A notação descreve crescimento, não tempo exato.
4. A pilha é LIFO: a ação mais recente sai primeiro. A fila é FIFO: o pedido que chegou primeiro sai primeiro.
5. `filter()` e `map()` criam novos arrays; o exemplo não precisa alterar `pedidos`. Com lista vazia, seleção e linhas resultam em `[]`; o agrupamento resulta em `{}`. A implementação deve usar acumulador inicial para que `reduce()` também funcione com array vazio.

</details>