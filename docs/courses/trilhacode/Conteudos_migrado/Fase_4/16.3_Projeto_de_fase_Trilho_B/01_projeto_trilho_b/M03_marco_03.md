---
arquivo_id: "f4-16-3-01-projeto-trilho-b-m03-marco-03"
parent_key: "16.3"
tipo_arquivo: "milestone"
assunto: "01_projeto_trilho_b"
ordem: 3
itens_origem: ["M3"]
titulo_marco: "Marco 3 — Produzir relatório e analisar a consulta"
---

### Marco 3 — Produzir relatório e analisar a consulta
**Entrega:** relatório de negócio, consulta reproduzível, plano `EXPLAIN` e justificativa dos índices.

Escolha uma consulta que responda a uma pergunta real. Registre os dados, filtros, ordenação, volume, versão/ambiente e plano observado. Use `EXPLAIN` e, quando adequado, `EXPLAIN ANALYZE`; lembre-se de que `ANALYZE` executa a consulta e adiciona sobrecarga de medição. Crie ou altere índice somente com hipótese ligada ao padrão de acesso. Compare planos ou tempos sob condições anotadas; custos estimados não equivalem a milissegundos nem garantem o mesmo resultado em outro ambiente.

**Foco conforme o tipo:**
- **T1:** relatório de vendas/estoque por evento ou período e consulta de pedidos.
- **T2:** agenda por tenant e período; evidencie filtro por tenant e a consulta de conflito/horário.
- **T4:** consulta filtrada e paginada com índice justificado; adicione cache Redis à consulta lenta, com TTL, chave que inclua os parâmetros relevantes e invalidação após mudança. Mostre hit, miss e a janela de desatualização; registre a comparação com e sem cache.
- **T5:** relatório agregado sobre a carga importada; meça consulta de relatório após uma carga representativa, sem misturar tempo de ingestão com tempo da consulta.

**Evidências sugeridas:** consulta SQL, resultado esperado, plano antes/depois se aplicável e tabela de medições.

