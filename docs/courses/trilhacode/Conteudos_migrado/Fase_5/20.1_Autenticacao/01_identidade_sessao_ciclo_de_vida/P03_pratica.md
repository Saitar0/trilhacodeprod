---
arquivo_id: "f5-20-1-01-identidade-sessao-ciclo-de-vida-p03-pratica"
parent_key: "20.1"
tipo_arquivo: "practice"
assunto: "01_identidade_sessao_ciclo_de_vida"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Implementação demonstrativa do ciclo de sessão
**Objetivo:** validar login, uso autenticado, renovação/expiração e logout sem criar primitivas próprias.

**Passos:**
1. Escolha biblioteca mantida ou provedor adequado ao projeto; implemente em ambiente local descartável.
2. Para sessão web, configure o cookie com atributos adequados, regenere o identificador ao autenticar e defina expiração server-side.
3. Para OAuth/OIDC ou refresh tokens, use a biblioteca/provedor e siga suas regras de PKCE, renovação e revogação; não escreva assinatura ou criptografia próprias.
4. Crie verificações para acesso sem login, sessão válida, expiração, logout e tentativa de reutilizar credencial encerrada.
5. Documente o que logout encerra e quais tokens podem permanecer válidos até expirar.

**Dica:** cookie e token têm comportamentos diferentes no navegador. Para cookie enviado automaticamente, descreva proteção CSRF; para token acessível ao JavaScript, descreva exposição a XSS e as alternativas arquiteturais consideradas.

