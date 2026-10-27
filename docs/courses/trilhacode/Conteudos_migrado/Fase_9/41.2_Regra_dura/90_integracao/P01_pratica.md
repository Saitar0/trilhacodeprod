---
arquivo_id: "f9-41-2-90-integracao-p01-pratica"
parent_key: "41.2"
tipo_arquivo: "practice"
assuntos: ["01_beneficio_fronteira", "02_custo_prontidao_operacional", "03_descoberta_teste_fronteira", "04_extracao_incremental_reversao"]
ordem: 1
itens_origem: ["P01"]
---


### Atividade 1 — ADR: manter, preparar ou extrair
**Contexto:** uma plataforma de pedidos tem módulos de checkout, catálogo e notificações no mesmo deploy. Durante picos, o envio de notificações aumenta o uso de CPU; duas equipes também fazem mudanças na área de pedidos, mas os incidentes ainda não foram separados por causa.

**Instruções:** escolha uma decisão inicial entre manter como está, reforçar fronteiras internas ou extrair uma capacidade. Liste quais dados faltam, proponha uma hipótese mensurável, compare pelo menos duas opções e registre benefício, custos, riscos, responsável, métricas e data/condição de revisão. Não presuma que notificação é automaticamente bom microsserviço.

**Entrega:** ADR de uma página e tabela de evidências observadas versus ainda desconhecidas.

**Dica gradual:** separe sintoma de causa; procure saber se a carga realmente interfere no checkout e se notificações têm regras e dados próprios. Compare também worker assíncrono no mesmo sistema e módulo isolado sem novo serviço.

