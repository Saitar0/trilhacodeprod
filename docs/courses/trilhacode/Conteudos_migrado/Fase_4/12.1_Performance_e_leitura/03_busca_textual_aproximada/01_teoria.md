---
arquivo_id: "f4-12-1-03-busca-textual-aproximada-01-teoria"
parent_key: "12.1"
tipo_arquivo: "theory"
assunto: "03_busca_textual_aproximada"
ordem: 3
itens_origem: ["4. Escolha a busca pelo tipo de correspondência"]
---

### 4. Escolha a busca pelo tipo de correspondência
A busca textual integrada do PostgreSQL transforma texto em lexemas normalizados e consulta termos com ranking. Ela é útil quando a pessoa procura palavras e quer resultados linguísticos relevantes. Uma coluna `tsvector) pode guardar o documento preparado; `tsquery) representa a consulta. GIN é um tipo de índice frequentemente usado para acelerar a busca textual.

```sql
SELECT id, titulo
FROM artigo
WHERE to_tsvector('portuguese', coalesce(titulo, '') || ' ' || coalesce(corpo, ''))
      @@ websearch_to_tsquery('portuguese', 'banco relacional');
```

A extensão `pg_trgm) divide strings em trigramas e ajuda a encontrar semelhanças ou correspondências parciais, como erros de digitação em nome de produto. Ela oferece operadores e índices GIN/GiST para usos compatíveis. Uma busca `LIKE '%texto%') sem índice adequado pode exigir varredura; o índice trigram pode ajudar dependendo do padrão e dos dados.

Busca textual e similaridade não são intercambiáveis: uma prioriza termos e normalização linguística; a outra mede sobreposição de fragmentos de caracteres. Um serviço dedicado de busca só deve ser avaliado quando requisitos de relevância, escala ou recursos justificarem a complexidade de sincronizar dados entre sistemas.

**Erro comum:** escolher o mecanismo pela palavra “busca” sem identificar se o requisito pede termos linguísticos, prefixo, substring ou tolerância a erro de digitação.

