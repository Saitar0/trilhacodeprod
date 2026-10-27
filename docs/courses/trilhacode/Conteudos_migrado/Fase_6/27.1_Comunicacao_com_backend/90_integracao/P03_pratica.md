---
arquivo_id: "f6-27-1-90-integracao-p03-pratica-md"
parent_key: "27.1"
tipo_arquivo: "practice"
assuntos: ["02_autenticacao_credenciais", "03_requisicao_vigente_paginacao", "04_cors_erros_integracao"]
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Escolha autenticação, paginação e CORS para um fluxo

**Desafio:** integre endpoint autenticado que usa paginação cursor-based e pode ser chamado em origem diferente em produção.

**Passos:**
1. Confirme contrato de autenticação: bearer no header ou cookie de sessão; não invente mecanismo.
2. Se for cookie, registre flags/configuração a confirmar com backend e defesa CSRF; se for bearer, determine como o frontend obtém token sem embutir segredo de servidor.
3. Leia e repasse cursor conforme contrato, respeitando hasMore e limit.
4. Liste configuração CORS do servidor para origem, método, Authorization ou credenciais que o navegador realmente enviará.
5. Faça uma chamada de primeira página, próxima página, sessão expirada e sem permissão; defina se retry é seguro e limitado.

**Dica:** um cursor não é necessariamente um número de página. E CORS não substitui autenticação nem autorização.

