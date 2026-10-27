---
arquivo_id: "f10-53-3-t04"
parent_key: "53.3"
tipo_arquivo: "theory"
assunto: "04_falhas_operacao_tradeoffs"
ordem: 4
itens_origem: ["### 4. Analisar falhas, operação e trade-offs"]
---


### 4. Analisar falhas, operação e trade-offs
Percorra pelo menos um caminho de sucesso e alguns de falha: timeout em dependência, pico acima da capacidade, indisponibilidade do banco, duplicação de mensagem, dado atrasado ou abuso de acesso. Para cada risco, explique detecção, contenção e recuperação. Retry sem limite pode piorar sobrecarga; use limites, backoff e idempotência quando apropriado. Métricas, logs e rastreamento devem ajudar a localizar falhas e medir objetivos relevantes.

Uma entrevista de system design é uma conversa iterativa. Apresente um baseline simples, pergunte qual requisito merece aprofundamento, identifique o gargalo mais plausível e atualize o desenho quando uma restrição mudar. Explique custo e consequências de cada escolha: cache reduz certas leituras, mas pode servir dados antigos; replicação pode melhorar disponibilidade/leitura, mas traz atraso e conflitos; particionamento pode distribuir carga, mas dificulta consultas e movimentação de dados. Não há desenho universal sem contexto.

