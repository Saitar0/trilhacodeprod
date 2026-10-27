---
arquivo_id: "f5-20-1-01-resumo"
parent_key: "20.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Autenticação verifica identidade; autorização decide acesso por ação e recurso.
- Sessões, tokens e JWT são conceitos diferentes; JWT assinado não oculta o payload nem resolve revogação.
- OAuth delega autorização; OIDC acrescenta identidade. Clientes públicos usam Authorization Code com PKCE.
- Cookies protegem alguns aspectos de armazenamento, mas seu envio automático exige considerar CSRF; JavaScript malicioso pode abusar da sessão.
- Renovação, expiração e logout precisam especificar quais credenciais e sessões são invalidadas.
- A arquitetura deve corresponder ao tipo de cliente e aos padrões atuais, com bibliotecas mantidas.

