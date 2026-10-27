---
arquivo_id: "f5-20-3-03-limites-de-abuso-e-recursos-01-teoria"
parent_key: "20.3"
tipo_arquivo: "theory"
assunto: "03_limites_de_abuso_e_recursos"
ordem: 3
itens_origem: ["Microtópico 3 — Limite abuso e consumo de recursos"]
---

## Microtópico 3 — Limite abuso e consumo de recursos
Rate limiting reduz a frequência de chamadas, mas uma política útil depende da rota e do custo. Considere combinar chaves como conta, sessão, token de cliente, endereço de rede confiável e operação; não use apenas IP como resposta universal, pois muitos usuários podem compartilhar um IP e atacantes podem distribuir chamadas. Em login e recuperação, limite tentativas sem criar um bloqueio fácil que permita negar serviço à vítima.

Rate limit é uma parte do controle de consumo. Defina também limites de tamanho de corpo e upload, quantidade máxima por página, número de itens em lote, timeout, concorrência e cotas de serviços pagos quando aplicável. Uma chamada pode custar muito mesmo abaixo de uma taxa geral. Em várias instâncias, contador apenas em memória não cria limite global; use armazenamento compartilhado ou controle no gateway apropriado.

Atrás de proxy, só confie em IP encaminhado se a cadeia de proxies estiver configurada para remover e substituir os headers recebidos e o app confiar apenas nos proxies corretos. Quando uma requisição excede o limite, responda de forma consistente, frequentemente com 429, e forneça orientação de retry quando fizer sentido.

**Exemplo:** uma API limita tentativas de envio de código por conta e por origem de rede, limita tamanho do arquivo e impõe teto de custo para o provedor de SMS. Os limites são calibrados ao fluxo legítimo e medidos em todas as instâncias.

**Erro comum:** aplicar limite global fixo por IP e acreditar que isso resolve abuso, scraping, upload excessivo ou operações caras.

**Checagem:** além da frequência, que recurso a operação pode esgotar? CPU, memória, armazenamento, serviço pago, mensagens, largura de banda ou concorrência podem exigir limites próprios.

