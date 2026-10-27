---
arquivo_id: "f8-39-1-01-sli-slo-sla-error-budget-p01-pratica-md"
parent_key: "39.1"
tipo_arquivo: "practice"
assunto: "01_sli_slo_sla_error_budget"
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Definir um SLI/SLO e interpretar o orçamento
Para um endpoint de consulta fictício, proponha um SLI baseado em requisições válidas concluídas com sucesso em até 300 ms. Defina a população, evento bom/ruim, fonte do sinal e janela. Use um alvo de exemplo de 99% por 28 dias e calcule a margem correspondente de eventos ruins. Explique por que esse alvo precisaria ser validado com produto e operação antes de ser adotado.

**Entrega:** definição do SLI e SLO em uma frase sem ambiguidade, regra de inclusão/exclusão e interpretação do error budget.

**Critérios de aceite:** unidade, população e janela estão declaradas; sucesso considera resposta e limite de latência; orçamento usa a mesma base; o texto distingue meta pedagógica de compromisso com usuário.

**Feedback esperado:** se o SLI for só CPU/memória, retorne à experiência que o serviço deveria entregar; se as exclusões alteram o denominador, documente-as.

