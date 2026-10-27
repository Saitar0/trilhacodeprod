---
arquivo_id: "f7-35-1-04-cache-isolamento-custos-01-teoria-md"
parent_key: "35.1"
tipo_arquivo: "theory"
assunto: "04_cache_isolamento_custos"
ordem: 4
itens_origem: ["### Microtópico 4 — Cache gerenciado, limites e custo"]
---

### Microtópico 4 — Cache gerenciado, limites e custo

**ElastiCache** oferece caches em memória gerenciados com engines como Valkey, Memcached e Redis OSS, conforme modalidade, versão, região e suporte atuais. A escolha considera compatibilidade do cliente/comandos, persistência ou replicação necessária, escalabilidade, conexão privada, operação e preço. Não escolha um engine só porque já conhece uma biblioteca: confirme suporte da oferta gerenciada e os recursos de que o sistema realmente precisa.

Cache reduz latência e carga quando há padrão de leitura apropriado; não substitui o banco como fonte durável do domínio. No padrão **cache-aside**, a aplicação lê cache; em ausência, busca no banco e preenche a chave com TTL. TTL limita a duração de entradas esquecidas, mas cria janela de dado desatualizado. Escrita no banco e invalidação/atualização de cache também podem falhar separadamente. Defina quais leituras toleram staleness, estratégia de invalidação e comportamento em cache indisponível. Não armazene no cache um valor que uma requisição não autorizada poderia reutilizar: inclua contexto de tenant/identidade na chave quando os dados forem isolados.

Custo pode incluir invocações/duração e concorrência de Lambda, chamadas/tipo de API Gateway, requests e armazenamento/transferência de SQS/SNS/EventBridge, logs, e nós/capacidade/armazenamento e tráfego de cache. Serviço gerenciado reduz algumas tarefas, não elimina monitoramento, sizing, segurança ou custo. Estime no pricing calculator com região, volume, tamanho e retenção; teste comportamento sob falha antes de optar por cache, fan-out ou processamento assíncrono.

