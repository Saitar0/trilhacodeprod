---
arquivo_id: "f5-20-1-03-oauth-oidc-e-arquitetura-cliente-p02-pratica"
parent_key: "20.1"
tipo_arquivo: "practice"
assunto: "03_oauth_oidc_e_arquitetura_cliente"
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Revisão de um fluxo OIDC/OAuth
**Objetivo:** reconhecer validações ausentes em um fluxo de cliente público.

**Passos:**
1. Use um diagrama didático de Authorization Code + PKCE ou a documentação de um provedor em ambiente de desenvolvimento.
2. Verifique client type, redirect URI cadastrada, desafio/verificador PKCE e proteção da transação com state/nonce conforme OIDC e o fluxo.
3. Identifique a finalidade de ID Token, access token e refresh token; indique qual componente valida cada um.
4. Revise o armazenamento e confirme que nenhum client secret está no bundle do navegador.
5. Registre três ameaças evitadas e duas responsabilidades que permanecem na aplicação.

**Dica:** uma integração OIDC delega autenticação ao provedor, mas a aplicação ainda precisa validar a resposta e manter sua própria sessão ou estratégia de acesso.

