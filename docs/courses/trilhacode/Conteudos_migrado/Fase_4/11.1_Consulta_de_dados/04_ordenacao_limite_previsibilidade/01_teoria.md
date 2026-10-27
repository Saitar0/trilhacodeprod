---
arquivo_id: "f4-11-1-04-ordenacao-limite-previsibilidade-01-teoria"
parent_key: "11.1"
tipo_arquivo: "theory"
assunto: "04_ordenacao_limite_previsibilidade"
ordem: 4
itens_origem: ["4. Ordene antes de limitar o resultado", "5. Leia consultas com segurança e previsibilidade"]
---

### 4. Ordene antes de limitar o resultado
ORDER BY define a ordem final. ASC é crescente e DESC decrescente. Sem ORDER BY, o banco pode retornar linhas em qualquer ordem; não assuma ordenação por chave primária, data de inserção ou ordem física.

Uma ordenação pode empatar. Acrescente uma coluna única como desempate quando for necessário ter uma sequência determinística, por exemplo `ORDER BY criado_em DESC, id DESC). No PostgreSQL, NULLs também têm posição definida pela ordenação padrão, mas você pode especificar `NULLS FIRST) ou `NULLS LAST) para explicitar a expectativa.

LIMIT restringe o número de linhas retornadas depois da ordenação. Para obter os dez pedidos mais recentes, ordene e limite juntos:

```sql
SELECT id, criado_em, total
FROM pedido
ORDER BY criado_em DESC, id DESC
LIMIT 10;
```

Sem uma ordem que diferencie os empates, quais linhas aparecem no limite pode variar. OFFSET pula linhas, mas páginas profundas podem ser caras e alterações simultâneas podem mover resultados; paginação por cursor/chave é aprofundada em outros contextos.

**Erro comum:** usar LIMIT 10 e esperar “os dez mais recentes” sem ordenar pela data.

### 5. Leia consultas com segurança e previsibilidade
Organize a consulta em uma forma legível: colunas selecionadas, fonte, filtros, ordenação e limite. Leia cada cláusula e preveja primeiro as linhas que sobrevivem ao WHERE; depois identifique as colunas projetadas, a ordem e o corte do LIMIT. Essa simulação ajuda a encontrar erro de lógica sem depender de adivinhação.

Quando valores vêm de usuário ou requisição, vincule-os por parâmetros preparados do driver/cliente. Não monte SQL concatenando texto não confiável. O formato do marcador depende da biblioteca usada (por exemplo, alguns drivers usam `$1)); placeholders são para valores, não substituem nomes dinâmicos de tabela ou coluna. Para ordenação escolhida pelo usuário, use uma lista permitida de opções no código.

**Erro comum:** interpolar entrada diretamente em uma string SQL e abrir caminho para injeção ou erros de aspas e tipos.

