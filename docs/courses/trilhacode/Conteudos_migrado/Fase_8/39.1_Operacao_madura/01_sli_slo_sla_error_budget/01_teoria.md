---
arquivo_id: "f8-39-1-01-sli-slo-sla-error-budget-01-teoria-md"
parent_key: "39.1"
tipo_arquivo: "theory"
assunto: "01_sli_slo_sla_error_budget"
ordem: 1
itens_origem: ["### Microtópico 1 — Medir o que importa: SLI, SLO, SLA e error budget"]
---

### Microtópico 1 — Medir o que importa: SLI, SLO, SLA e error budget

Um **SLI** (*service level indicator*) é uma medida quantitativa de uma dimensão do serviço que importa para quem o utiliza. Exemplos incluem a proporção de requisições válidas que terminam com sucesso, a latência dessas requisições ou a proporção de tarefas processadas no prazo. Defina população, evento bom/ruim, fonte dos dados e janela de medição. Uma métrica de CPU pode ajudar a explicar um problema, mas não substitui um indicador de experiência se a pergunta é se a pessoa conseguiu concluir a ação.

Um **SLO** (*service level objective*) é o alvo para um SLI em uma janela definida. Exemplo didático, não promessa de produto: “em uma janela móvel de 28 dias, pelo menos 99% das requisições válidas de consulta retornam sucesso em até 300 ms”. A definição precisa esclarecer o que conta como requisição válida, como latência é medida e quais exclusões existem. Escolher o alvo exige contexto de produto, capacidade e expectativa; não copie um número sem justificativa.

Um **SLA** (*service level agreement*) é um acordo de nível de serviço com usuários ou partes interessadas que define compromissos e consequências caso não sejam cumpridos. Pode envolver créditos ou outras obrigações. O SLO pode ser um objetivo operacional interno sem consequências contratuais. Se alguém usar os termos como sinônimos, pergunte: “há um acordo e o que acontece se o alvo não for atingido?”.

O **error budget** é a margem de eventos ruins permitida pela meta para a janela definida. Em um SLO de 99% de eventos bons, o orçamento corresponde a até 1% de eventos ruins segundo a mesma população e período. O orçamento ajuda a decidir quando reduzir o ritmo de mudanças, investigar confiabilidade ou investir em prevenção. Não é autorização para causar falhas; é uma forma explícita de discutir risco junto com entrega de mudanças.

