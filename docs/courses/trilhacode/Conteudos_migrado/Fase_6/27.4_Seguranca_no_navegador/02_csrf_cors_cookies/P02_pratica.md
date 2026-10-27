---
arquivo_id: "f6-27-4-02-csrf-cors-cookies-p02-pratica-md"
parent_key: "27.4"
tipo_arquivo: "practice"
assunto: "02_csrf_cors_cookies"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Modelo de ameaça CSRF para uma sessão
**Contexto e objetivo:** diferenciar envio automático de cookie, uso de token e controle de origem sem atacar sites reais.

**Cenário:** aplicação local tem `POST /profile/email` que altera o e-mail; autenticação por cookie de sessão; formulário legítimo envia JSON e a aplicação aceita origens configuradas.

**Instruções:** desenhe browser, site legítimo e site externo; marque quais credenciais o browser envia automaticamente. Escolha defesas compatíveis: `SameSite` adequado ao fluxo, token CSRF e/ou validação de `Origin`/`Referer`, além de autorização e método/status corretos. Explique quando um cabeçalho customizado e preflight são úteis, sem tratá-los como garantia universal. Escreva testes de desenho (origem esperada, origem não permitida, token ausente/inválido) em ambiente local ou use uma matriz de requisições fictícias, sem enviar tráfego a terceiros.

**Entrega:** diagrama/ameaça, decisão e justificativa de cada defesa, e matriz com esperado para requisições autenticada legítima, cross-site sem proteção, token inválido e usuário sem permissão.

**Dica gradual:** `HttpOnly` não impede que o cookie seja enviado; pergunte se o atacante consegue induzir o browser a fazer uma requisição com a sessão. Em seguida avalie quais controles o servidor consegue verificar.

**Feedback e erro comum:** a resposta separa CSRF de XSS e CORS e identifica autenticação/autorização no servidor. Erro comum: dizer “tem CORS” ou “cookie HttpOnly” como defesa suficiente sem analisar credenciais automáticas e validação da operação.

