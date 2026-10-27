---
arquivo_id: "f5-19-1-02-consultas-relacoes-custo-01-teoria"
parent_key: "19.1"
tipo_arquivo: "theory"
assunto: "02_consultas_relacoes_custo"
ordem: 2
itens_origem: ["Microtópico 2 — Consultas, relações e custo"]
---

## Microtópico 2 — Consultas, relações e custo
Use filtros, ordenação, paginação e projeção para pedir somente o conjunto necessário. Carregar relações não é gratuito: dependendo da estratégia e da ferramenta, a leitura pode gerar joins, consultas adicionais ou múltiplas consultas. N+1 acontece quando a aplicação busca uma lista e depois dispara uma consulta por item para obter dados relacionados; observe tanto o número de consultas quanto o volume de linhas e colunas.

Inspecione o SQL emitido e meça com dados representativos. Uma contagem baixa de consultas não garante uma consulta barata: joins podem multiplicar linhas, uma projeção ampla pode transferir dados demais e a ausência de índice pode causar varredura. Para consultas relevantes, compare plano de execução, cardinalidade, índices e latência no banco usado pelo projeto.

**Exemplo:** listar 30 autores e, em um loop, buscar os artigos de cada autor tende a produzir uma consulta inicial e até 30 consultas relacionadas. Prefira uma leitura relacional apropriada ou uma estratégia em lote; confirme a forma efetiva no log do ORM, pois a execução varia por ferramenta, versão, banco e configuração.

**Erro comum:** aplicar carregamento antecipado de todas as relações para “resolver N+1”. Isso pode trocar muitas consultas pequenas por uma consulta enorme e dados que a tela nem usa.

**Checagem:** ao investigar N+1, que evidência coleta? O número e o formato das consultas geradas para uma quantidade conhecida de registros, além do volume e do plano quando necessário.

