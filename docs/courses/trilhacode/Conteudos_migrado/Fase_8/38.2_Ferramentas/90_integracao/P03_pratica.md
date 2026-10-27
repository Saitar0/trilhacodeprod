---
arquivo_id: "f8-38-2-90-integracao-p03-pratica-md"
parent_key: "38.2"
tipo_arquivo: "practice"
assuntos: ["01_fluxo_otel_prometheus_promql", "02_grafana_dashboards_operacao"]
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Simular incidente e definir resposta
Introduza uma lentidão e um aumento controlado de respostas 5xx no serviço de exemplo. Observe a sequência do sintoma no dashboard, identifique a rota afetada, encontre o span/log relacionado se estiverem instrumentados e proponha um alerta. Se escolher uma plataforma gerenciada como New Relic, compare-a com o caminho local em termos de dados enviados, ingestão, retenção, custo, acesso e saída/portabilidade.

**Entrega:** hipótese de causa com evidências, regra de alerta com condição/janela/ação, passo a passo para investigação e uma comparação curta de backend local versus gerenciado.

**Critérios de aceite:** diferencia sintoma de causa comprovada; alerta evita variações transitórias quando apropriado, indica responsável e próximo passo; comparação inclui ingestão, retenção e tratamento de dados; não envia segredo ou dado pessoal.

**Feedback esperado:** dashboard mostra o comportamento agregado, trace/span ajuda a localizar uma execução e logs fornecem detalhes do evento; um alerta útil orienta o que fazer e não apenas afirma que um gráfico mudou.

