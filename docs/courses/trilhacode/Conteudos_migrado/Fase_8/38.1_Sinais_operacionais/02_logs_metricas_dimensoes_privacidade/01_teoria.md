---
arquivo_id: "f8-38-1-02-logs-metricas-dimensoes-privacidade-01-teoria-md"
parent_key: "38.1"
tipo_arquivo: "theory"
assunto: "02_logs_metricas_dimensoes_privacidade"
ordem: 2
itens_origem: ["### Microtópico 2 — Criar sinais que possam ser analisados"]
---

### Microtópico 2 — Criar sinais que possam ser analisados

Um log estruturado tem **esquema estável**: campos com nomes, tipos e significados consistentes. JSON pode ser um formato conveniente, mas JSON por si só não torna o registro estruturado se cada mensagem tiver campos imprevisíveis. Um conjunto inicial útil pode incluir `timestamp`, `severity`, `service.name`, `deployment.environment.name`, rota normalizada, resultado e duração. Registre a exceção necessária para investigação, sem despejar a requisição inteira.

Métricas devem representar perguntas agregadas. Em uma API, exemplos são requisições por rota normalizada e código de resultado, duração por rota e saturação de recursos. Labels com valores imprevisíveis — como `user_id`, email, URL completa, ID de pedido ou texto de erro — criam muitas séries temporais. Essa **alta cardinalidade** aumenta custo e dificulta consultas; além disso, valores pessoais ou secretos podem vazar para a telemetria. Use dimensões limitadas e úteis; mantenha identificadores de uma operação em logs ou traces somente quando houver justificativa, proteção e política de retenção.

Não registre tokens, senhas, cabeçalhos de autenticação, corpos completos ou dados pessoais sem necessidade autorizada. Aplique minimização, redação/mascaramento, controles de acesso e retenção compatíveis com o uso. Telemetria também é dado produzido e armazenado: deve entrar no desenho de segurança e privacidade.

