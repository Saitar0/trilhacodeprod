---
arquivo_id: "f5-24-4-m02-base-da-fase-5-api-autenticacao-e-postgresql"
parent_key: "24.4"
tipo_arquivo: "milestone"
ordem: 2
itens_origem: ["M2"]
titulo_marco: "Marco 2 — Base da Fase 5: API, autenticação e PostgreSQL"
---

### Marco 2 — Base da Fase 5: API, autenticação e PostgreSQL
**Objetivo:** criar uma base autocontida que permita testar a regra sem depender de infraestrutura real.

**Tarefas:** implemente migrations, API, autenticação e persistência para o fluxo mínimo. Valide entradas, aplique autorização no servidor e defina respostas de sucesso/erro. Use segredo local ignorado pelo Git e `.env.example` seguro. Não confie em `ownerId`, `tenantId` ou papel fornecido livremente no corpo para conceder acesso.

**Evidência:** migration aplicável a banco vazio, código da rota/regra, exemplos de requisição e resposta, seed sintético e comandos para iniciar banco/API.

**Dica:** teste autorização com uma sessão válida que tenta acessar objeto de outra pessoa/tenant. Um 401 para usuário anônimo não prova isolamento entre objetos.

