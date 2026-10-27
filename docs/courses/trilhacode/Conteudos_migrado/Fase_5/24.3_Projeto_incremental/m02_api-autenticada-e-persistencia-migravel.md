---
arquivo_id: "f5-24-3-m02-api-autenticada-e-persistencia-migravel"
parent_key: "24.3"
tipo_arquivo: "milestone"
ordem: 2
itens_origem: ["M2"]
titulo_marco: "Marco 2 — API autenticada e persistência migrável"
---

### Marco 2 — API autenticada e persistência migrável
**Objetivo:** entregar a operação principal com validação, autenticação/autorização e PostgreSQL real.

**Tarefas:** implemente controller/rota, serviço/regra de domínio e persistência; valide entrada na fronteira; obtenha a identidade do usuário a partir da sessão/token validado; aplique autorização no servidor; inclua migration e dados sintéticos de demonstração, se necessários. Retorne erros consistentes sem expor detalhes internos.

**Evidência:** código da rota e regra, migration aplicada a banco vazio, exemplos de requisição/resposta e teste ou demonstração reproduzível para sucesso, entrada inválida e acesso negado.

**Dica:** derive o proprietário da identidade autenticada e passe essa identidade para a consulta. Se o domínio for multiusuário, teste também um identificador de recurso que pertence a outra pessoa.

