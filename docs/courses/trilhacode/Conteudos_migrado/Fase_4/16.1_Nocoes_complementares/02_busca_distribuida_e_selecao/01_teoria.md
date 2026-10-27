---
arquivo_id: "f4-16-1-02-busca-distribuida-e-selecao-01-teoria"
parent_key: "16.1"
tipo_arquivo: "theory"
assunto: "02_busca_distribuida_e_selecao"
ordem: 2
itens_origem: ["2. Busca e análise", "3. Como comparar sem escolher por rótulo"]
---

### 2. Busca e análise
Elasticsearch é um mecanismo distribuído de busca e análise que trabalha com documentos indexados. A análise do texto e o índice invertido ajudam a encontrar termos e ordenar resultados por relevância; agregações resumem grupos de documentos. Mudanças indexadas podem levar um intervalo até ficarem pesquisáveis, portanto o fluxo de escrita e a necessidade de atualização imediata precisam entrar na decisão. [Elastic — busca textual](https://www.elastic.co/docs/solutions/search/full-text/how-full-text-works) e [agregações](https://www.elastic.co/docs/explore-analyze/query-filter/aggregations).

Elasticsearch pode complementar um banco transacional: a aplicação mantém dados principais na fonte apropriada e projeta para o índice os campos necessários à busca. Essa projeção introduz sincronização e possível atraso entre a origem e o resultado de pesquisa. Não escolha uma tecnologia apenas por pertencer à categoria “NoSQL”; compare consultas, consistência esperada, integração, custos e capacidade de operação.

### 3. Como comparar sem escolher por rótulo
Comece por requisitos concretos: consultas que precisam ser rápidas, filtros e ordenações, volume e distribuição dos dados, tolerância a atraso, transações, forma de integração, custos e experiência da equipe. Depois teste o caminho crítico com dados representativos e verifique índices, limites e custos na documentação atual do serviço e da região/plano escolhidos. Os três sistemas não são substitutos diretos: a escolha depende do problema e do papel de cada componente.

