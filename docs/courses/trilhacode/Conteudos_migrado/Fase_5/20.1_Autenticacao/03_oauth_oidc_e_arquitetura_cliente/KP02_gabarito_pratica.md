---
arquivo_id: "f5-20-1-03-oauth-oidc-e-arquitetura-cliente-kp02-gabarito-pratica"
parent_key: "20.1"
tipo_arquivo: "answer_key_pratica"
assunto: "03_oauth_oidc_e_arquitetura_cliente"
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** fluxo usa Authorization Code + PKCE para cliente público, correspondência exata de redirect cadastrada, valida associação da resposta e distingue tokens. Não inclui segredo estático no cliente e reconhece que XSS/CSRF continuam exigindo controles apropriados.

