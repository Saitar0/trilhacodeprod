---
arquivo_id: "f8-38-1-90-integracao-p03-pratica-md"
parent_key: "38.1"
tipo_arquivo: "practice"
assuntos: ["01_escolha_dos_sinais", "02_logs_metricas_dimensoes_privacidade"]
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Revisar dimensões e privacidade
Avalie as possíveis dimensões de uma métrica de requisições: `method`, rota normalizada, código HTTP, `user_id`, email, URL completa e texto livre do erro. Classifique cada uma como útil e controlada, candidata a log/trace sob política, ou a remover. Depois proponha um sinal e uma consulta/agrupamento para investigar aumento de erros por rota.

**Entrega:** classificação justificada, métrica revisada e uma regra de coleta/retention a discutir com a equipe.

**Critérios de aceite:** rota e status são dimensões limitadas; IDs pessoais, URL irrestrita e texto livre não viram labels; a investigação continua possível sem indexar esses valores; reconhece controles de acesso e retenção.

**Feedback esperado:** dimensões úteis para depuração nem sempre são adequadas para métricas. Escolha o sinal e a granularidade conforme a pergunta, custo e risco de exposição.

