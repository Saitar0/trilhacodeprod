---
arquivo_id: "f4-15-1-01-cache-aside-chaves-01-teoria"
parent_key: "15.1"
tipo_arquivo: "theory"
assunto: "01_cache_aside_chaves"
ordem: 1
itens_origem: ["1. Estruturas de dados e formato de acesso", "2. Cache-aside: consulta, falta e preenchimento"]
---

## Teoria

### 1. Estruturas de dados e formato de acesso
Redis oferece estruturas com comportamentos diferentes. Strings atendem valores simples e dados serializados; hashes organizam campos de um registro; listas mantêm sequência; sets guardam itens únicos sem ordem; sorted sets associam uma pontuação a cada item para consultas ordenadas. A escolha deve partir das operações que a aplicação precisa fazer. Por exemplo, um ranking combina bem com sorted set; usar lista para uma consulta de pertencimento não oferece a mesma semântica de um set. Estruturas mais especializadas também têm custos de memória e operação diferentes. [Redis — tipos de dados](https://redis.io/docs/latest/develop/data-types/) e [comparação de tipos](https://redis.io/docs/latest/develop/data-types/compare-data-types/).

### 2. Cache-aside: consulta, falta e preenchimento
No padrão cache-aside, a aplicação consulta Redis primeiro. Se encontra a chave (cache hit), usa o valor; se não encontra (cache miss), consulta a fonte de verdade, devolve o resultado e grava uma cópia no cache. Exemplo de chave: `catalogo:categoria:livros:pagina:1`. Ela precisa identificar todos os parâmetros que alteram a resposta; omitir página, idioma, usuário ou versão pode misturar resultados diferentes. Para respostas serializadas, defina um formato e trate erros de leitura ou desserialização.

Um TTL pode ser definido no próprio `SET`, por exemplo `SET catalogo:categoria:livros:pagina:1 "<json>" EX 300`, que expira em 300 segundos. TTL limita a permanência prevista da cópia, mas não assegura atualização imediata: uma escrita na origem pode deixar a resposta antiga no cache até ocorrer invalidação ou expiração. Cache-aside carrega apenas dados solicitados e mantém a fonte principal como autoridade. [Redis — cache-aside](https://redis.io/docs/latest/develop/use-cases/cache-aside/) e [comando SET](https://redis.io/docs/latest/commands/set/).

