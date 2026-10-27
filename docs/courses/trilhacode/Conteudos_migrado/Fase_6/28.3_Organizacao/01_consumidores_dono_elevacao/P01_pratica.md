---
arquivo_id: "f6-28-3-01-consumidores-dono-elevacao-p01-pratica-md"
parent_key: "28.3"
tipo_arquivo: "practice"
assunto: "01_consumidores_dono_elevacao"
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Faça uma auditoria de localização de estado
**Objetivo:** identificar dados redundantes e escolher o proprietário apropriado para cada estado.

**Passos:**
1. Escolha uma tela com formulário, navegação, modal, lista e filtros, ou use um catálogo de produtos com favoritos.
2. Liste os valores mantidos hoje, seus leitores, quem pode alterá-los e sua origem.
3. Marque valores derivados, cópias de dados remotos e estados duplicados entre componentes.
4. Proponha uma localização para cada estado: componente, ancestral comum, Context/store, URL ou cache remoto; registre a evidência que justifica cada decisão.
5. Identifique um requisito que faria cada decisão importante mudar, como compartilhar filtro por link ou manter um rascunho ao navegar.

**Dica:** conte fatos, não hooks. Dois estados `useState` diferentes podem representar uma só decisão; uma store global também pode conter vários domínios sem que todos precisem ser globais.

**Entrega:** mapa de consumidores e tabela “atual → proposta → motivo → gatilho de revisão”.

**Critérios de conclusão:** cada fato tem um proprietário; valores derivados não ficam armazenados sem motivo; propostas citam requisitos observáveis.

