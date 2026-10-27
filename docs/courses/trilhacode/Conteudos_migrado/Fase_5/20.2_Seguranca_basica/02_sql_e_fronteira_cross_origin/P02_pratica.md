---
arquivo_id: "f5-20-2-02-sql-e-fronteira-cross-origin-p02-pratica"
parent_key: "20.2"
tipo_arquivo: "practice"
assunto: "02_sql_e_fronteira_cross_origin"
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Consulta e configuração cross-origin
**Objetivo:** corrigir SQL dinâmico inseguro e separar comportamento de CORS dos controles do servidor.

**Passos:**
1. Use uma busca demonstrativa que filtre por termo e aceite ordenação escolhida pela interface.
2. Vincule o termo como parâmetro; converta ordenação para mapa de colunas permitidas.
3. Configure origens cross-origin necessárias, distinguindo chamadas públicas sem credenciais de chamadas credenciadas.
4. Teste uma origem permitida e uma origem não permitida em navegador e explique por que curl não é limitado por CORS.
5. Verifique que o endpoint ainda autentica/autoriza no servidor e não depende da lista CORS como controle de acesso.

**Dica:** não reflita o header Origin sem comparar com a lista configurada. Com credenciais, a resposta deve indicar uma origem explícita aprovada, não wildcard.

