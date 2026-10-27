---
arquivo_id: "f5-20-1-03-oauth-oidc-e-arquitetura-cliente-01-teoria"
parent_key: "20.1"
tipo_arquivo: "theory"
assunto: "03_oauth_oidc_e_arquitetura_cliente"
ordem: 3
itens_origem: ["Microtópico 4 — OAuth 2.0 e OpenID Connect", "Microtópico 6 — Escolha uma arquitetura coerente com o cliente"]
---

## Microtópico 4 — OAuth 2.0 e OpenID Connect
OAuth 2.0 é um framework de autorização delegada. OpenID Connect (OIDC) adiciona uma camada de autenticação e identidade sobre OAuth. Quando o objetivo é permitir que uma pessoa entre usando um provedor, use uma integração OIDC adequada; não trate OAuth isolado como protocolo de login.

Para clientes públicos, como aplicativos nativos e código JavaScript entregue ao navegador, use Authorization Code com PKCE. O cliente público não consegue guardar um segredo compartilhado embutido no código. Cadastre e valide URIs de redirecionamento exatas. Proteja a associação entre a transação iniciada e a resposta com PKCE e, conforme o fluxo OIDC e o uso de estado da aplicação, valide state e nonce apropriadamente. Não ensine Implicit Grant como caminho padrão.

A integração delega tarefas sensíveis ao provedor, mas exige validação dos tokens e das respostas de acordo com a especificação. Use uma biblioteca mantida e configure a confiança no emissor e nas chaves; não implemente primitivas criptográficas ou validação improvisada.

**Exemplo:** uma aplicação web inicia Authorization Code + PKCE, valida a resposta da mesma transação e, após confirmar a identidade via OIDC, cria uma sessão de aplicação ou usa a arquitetura de tokens planejada.

**Erro comum:** colocar um client secret em um bundle JavaScript ou aceitar qualquer redirect URI. O código entregue ao navegador é público e o redirecionamento precisa corresponder ao que foi registrado.

**Checagem:** qual protocolo responde à pergunta “quem autenticou?” e qual trata concessão de acesso delegado? OIDC adiciona identidade; OAuth trata autorização delegada.

## Microtópico 6 — Escolha uma arquitetura coerente com o cliente
Para uma aplicação web de domínio próprio, uma sessão de servidor com cookie pode ser suficiente. Para uma aplicação que delega acesso a APIs por OAuth, avalie padrões atuais para aplicações de navegador, como Backend for Frontend (BFF), token-mediating backend ou cliente OAuth executado no próprio navegador. Eles distribuem responsabilidades e riscos de forma diferente; não existe um padrão único que elimine XSS, CSRF ou roubo de credenciais.

BFF mantém tokens OAuth no backend e expõe ao navegador uma sessão via cookie; isso reduz a exposição direta dos tokens, mas o cookie exige defesa contra CSRF e o BFF precisa ser protegido. Um cliente OAuth no navegador é um cliente público e seu código pode ser inspecionado; PKCE é obrigatório, credenciais acessíveis ao JavaScript elevam o impacto de XSS e escopo/vida dos tokens devem ser limitados. Considere também CORS, origens, implantação, provedores e capacidade operacional. A recomendação específica deve seguir a arquitetura e a orientação atual do protocolo.

Desenhe a sequência de login, callback, requisição autenticada, renovação e logout. Marque onde cada credencial é criada, transportada, armazenada, validada e invalidada. Essa representação expõe lacunas antes de implementar.

**Exemplo:** um BFF usa cookie seguro de sessão para o navegador e guarda tokens do provedor no backend. Uma SPA pode ser cliente OAuth público com Authorization Code + PKCE. Compare a superfície de ataque e a operação necessárias para o produto em questão.

**Erro comum:** concluir que HttpOnly torna o sistema imune a XSS, ou que token em armazenamento acessível por JavaScript é seguro apenas por ser JWT.

**Checagem:** o diagrama deixa explícito quem recebe cada credencial e qual defesa cobre envio automático de cookie, leitura de token e resposta do provedor?

