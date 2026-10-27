---
arquivo_id: "f10-48-1-t04"
parent_key: "48.1"
tipo_arquivo: "theory"
assunto: "04_custo_e_limites"
ordem: 4
itens_origem: ["### 4. Estimar custo e acompanhar limites"]
---


### 4. Estimar custo e acompanhar limites
Para uma estimativa inicial, use quantidade esperada de solicitações × unidades de entrada e saída por solicitação × preço vigente de cada unidade. A fórmula deve refletir a tarifa publicada e os recursos usados; algumas ofertas podem cobrar por tokens, chamadas de ferramenta, imagem, áudio, processamento em lote ou capacidade implantada. Não use preço antigo ou de outro canal/região como se fosse atual.

Trate a conta como hipótese. Faça amostra, registre contadores agregados de uso, latência e erro, estabeleça limites por usuário/fluxo e revise a projeção com tráfego real. Evite guardar prompts e respostas para calcular custo: prefira metadados necessários e contagens retornadas, com política de retenção. Este módulo introduz a fronteira e a avaliação; timeout, fallback, circuit breaker e operação são aprofundados em 48.2.

