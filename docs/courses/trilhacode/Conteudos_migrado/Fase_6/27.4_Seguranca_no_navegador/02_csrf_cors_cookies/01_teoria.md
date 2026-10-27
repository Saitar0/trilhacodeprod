---
arquivo_id: "f6-27-4-02-csrf-cors-cookies-01-teoria-md"
parent_key: "27.4"
tipo_arquivo: "theory"
assunto: "02_csrf_cors_cookies"
ordem: 2
itens_origem: ["### 3. Distinguir XSS, CSRF, CORS e atributos de cookie"]
---

### 3. Distinguir XSS, CSRF, CORS e atributos de cookie
Cross-site request forgery (CSRF) usa o fato de que o navegador pode enviar credenciais automaticamente — em especial cookies de sessão — junto a uma requisição induzida por outro site. A defesa depende do desenho: token anti-CSRF, validação de origem, `SameSite` apropriado e ausência de efeitos colaterais em métodos de leitura podem compor a proteção. Nenhuma opção deve ser aplicada como ritual sem entender navegador, domínio, subdomínios, fluxo de login e endpoints.

`HttpOnly` impede acesso ao cookie por JavaScript, mas não impede que o navegador o envie em uma requisição. `Secure` limita envio a conexões HTTPS. `SameSite` pode reduzir envio em contextos cross-site, com comportamento dependente da configuração e dos fluxos. Essas propriedades não substituem autorização no servidor.

CORS é uma política do navegador para controlar se código de uma origem pode ler certas respostas; não autentica usuário e não bloqueia universalmente que outro site tente enviar requisições. Também não é substituto de token CSRF quando credenciais são enviadas automaticamente. Bearer token guardado em `localStorage` não é anexado automaticamente pelo browser como cookie, mas qualquer script executado na mesma origem pode lê-lo; XSS pode capturar ou usar credenciais acessíveis à página. Token em memória reduz persistência, mas não impede que um script malicioso atue enquanto a sessão estiver aberta.

