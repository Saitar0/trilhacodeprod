---
arquivo_id: "f6-27-1-90-integracao-p01-pratica-md"
parent_key: "27.1"
tipo_arquivo: "practice"
assuntos: ["01_contrato_requisicao_resposta", "04_cors_erros_integracao"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Construa um cliente de lista que modele erros

**Desafio:** implemente a busca paginada de pedidos obedecendo ao contrato da API e sem confundir erro HTTP com falha de rede.

**Passos:**
1. Registre método, URL, parâmetros, headers, autenticação e formato de resposta do endpoint de pedidos.
2. Envie Accept e o header de autenticação somente se o mecanismo e o contrato os exigirem.
3. Verifique response.ok/status antes de assumir sucesso; trate resposta sem corpo se o endpoint puder retornar 204.
4. Converta erros estruturados conhecidos em estados seguros para a UI e mantenha uma categoria separada para rede/CORS/JSON inválido.
5. Teste em ambiente local 200 com dados, 200 vazio, 401, 403, 500 e falha de rede; confira que URL não contém token.

**Dica:** não apresente texto técnico do backend sem filtragem e não tente interpretar como JSON toda resposta.

