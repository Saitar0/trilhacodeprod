---
arquivo_id: "f4-12-1-02-indices-custo-escrita-01-teoria"
parent_key: "12.1"
tipo_arquivo: "theory"
assunto: "02_indices_custo_escrita"
ordem: 2
itens_origem: ["3. Escolha índices conforme filtros e escrita"]
---

### 3. Escolha índices conforme filtros e escrita
Um índice é uma estrutura auxiliar que pode reduzir trabalho de leitura, ao custo de armazenamento e manutenção em INSERT, UPDATE e DELETE. B-tree atende muitos casos de igualdade, comparação por intervalo e ordenação; outros tipos atendem operadores específicos. Se uma consulta filtra por `categoria_id) e ordena por `criado_em), um índice composto pode ser uma hipótese, mas a ordem das colunas e os filtros realmente usados precisam ser avaliados.

A seletividade descreve quantas linhas o filtro tende a retornar. Se quase todas as linhas correspondem, ler a tabela inteira pode custar menos do que saltar do índice para muitas páginas. Um índice pode também não servir quando a consulta transforma a coluna de modo incompatível com o índice existente.

```sql
CREATE INDEX produto_categoria_criado_idx
  ON produto (categoria_id, criado_em DESC);

EXPLAIN
SELECT id, criado_em
FROM produto
WHERE categoria_id = 7
ORDER BY criado_em DESC
LIMIT 20;
```

O índice acima é apenas uma hipótese para essa consulta e esse padrão. Meça em dados de volume e distribuição adequados; depois avalie também o custo adicional das escritas e o espaço ocupado.

**Erro comum:** criar um índice composto sem considerar quais colunas aparecem nos filtros e na ordenação ou esperar que ele melhore todas as consultas.

