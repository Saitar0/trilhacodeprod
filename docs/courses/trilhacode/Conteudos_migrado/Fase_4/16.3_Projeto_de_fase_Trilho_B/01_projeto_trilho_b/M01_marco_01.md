---
arquivo_id: "f4-16-3-01-projeto-trilho-b-m01-marco-01"
parent_key: "16.3"
tipo_arquivo: "milestone"
assunto: "01_projeto_trilho_b"
ordem: 1
itens_origem: ["M1"]
titulo_marco: "Marco 1 — Escolher o problema e desenhar o modelo"
---

## Plano de entregas

### Marco 1 — Escolher o problema e desenhar o modelo
**Entrega:** decisão de tipo, pergunta de negócio, operações de dados e diagrama ER inicial.

Escreva em poucas linhas qual situação o projeto resolve e qual regra técnica precisa ser demonstrada. Liste as leituras e escritas que a fatia precisa suportar. Desenhe as entidades, chaves e relações necessárias; anote constraints e índices que talvez sejam necessários e por quê. Selecione dados de exemplo com distribuição suficiente para que a consulta e o relatório tenham significado. Declare o que fica fora do escopo.

**Foco conforme o tipo:**
- **T1:** evento, lote/ingresso, pedido e pagamento; a regra é impedir venda acima do estoque em operações concorrentes.
- **T2:** tenant, usuários/papéis e agenda; toda consulta de domínio é limitada ao tenant e horários incompatíveis não se sobrepõem para o recurso correspondente.
- **T4:** catálogo/receitas e campos de busca/filtro; defina consulta, filtros, ordenação, paginação e um critério de relevância ou latência.
- **T5:** formato e volume do CSV, destino relacional, regras de validação e pergunta do relatório; separe registros aceitos e rejeitados de forma explicável.

**Evidências sugeridas:** decisão no README, diagrama e tabela de operações/regra/entidade.

