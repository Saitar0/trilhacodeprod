---
arquivo_id: "f8-38-2-02-grafana-dashboards-operacao-01-teoria-md"
parent_key: "38.2"
tipo_arquivo: "theory"
assunto: "02_grafana_dashboards_operacao"
ordem: 2
itens_origem: ["### Microtópico 3 — Fazer Grafana responder a uma pergunta", "### Microtópico 4 — Avaliar integração, volume e operação"]
---

### Microtópico 3 — Fazer Grafana responder a uma pergunta

Grafana conecta-se a um data source, por exemplo Prometheus, e cada painel contém consulta, visualização e configuração. Antes de escolher gráfico, escreva a pergunta. Um painel de visão geral pode exibir taxa de requisições, proporção de erros, p95 e saturação; um painel de diagnóstico pode oferecer filtro por serviço/rota e links para traces quando a integração estiver configurada.

Todo painel precisa tornar seu resultado interpretável: título em forma de pergunta, unidade, janela temporal, agrupamento, filtros úteis e comportamento esperado. Gráficos sem unidade, escala ou contexto temporal podem induzir a conclusões ruins. Evite duplicar a mesma informação em muitos painéis e não apresente percentis como se fossem médias.

Alertas devem identificar uma condição acionável, persistente pelo tempo necessário e ligada a impacto ou sintoma relevante. Defina nome, expressão, janela, limiar, destinatário e instrução de investigação. Threshold arbitrário ou alerta em cada variação pequena gera ruído. A política de notificação e a regra de alerta podem residir no Prometheus/Alertmanager ou no Grafana, conforme a arquitetura; não configure dois caminhos redundantes sem uma razão e sem saber quem notifica.

### Microtópico 4 — Avaliar integração, volume e operação

Uma plataforma gerenciada pode reduzir a operação de armazenamento e consulta, mas não elimina instrumentação, decisões de dados ou controle de custo. Integração OTLP, retenção, ingestão cobrada, limites de cardinalidade, amostragem, autenticação, rede, localização e exportação dos dados variam por produto e plano. Compare o custo estimado para volumes reais e teste quais campos chegam ao destino antes de enviar dados de produção.

Em qualquer stack, monitore o próprio pipeline: alvo fora do ar, scrape atrasado, fila de exportação, falhas de exportação e ausência inesperada de sinais. Telemetria incompleta pode fazer um painel parecer saudável enquanto dados não estão chegando. Documente o caminho e a responsabilidade de cada etapa; altere uma variável por vez ao depurar conexão ou configuração.

