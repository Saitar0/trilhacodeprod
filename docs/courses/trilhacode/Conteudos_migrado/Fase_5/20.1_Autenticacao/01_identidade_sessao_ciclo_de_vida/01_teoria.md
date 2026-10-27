---
arquivo_id: "f5-20-1-01-identidade-sessao-ciclo-de-vida-01-teoria"
parent_key: "20.1"
tipo_arquivo: "theory"
assunto: "01_identidade_sessao_ciclo_de_vida"
ordem: 1
itens_origem: ["Microtópico 1 — Identidade, autenticação e autorização", "Microtópico 2 — Sessão no servidor", "Microtópico 5 — Renovação, expiração e encerramento"]
---

## Microtópico 1 — Identidade, autenticação e autorização
Identidade representa a entidade reconhecida pelo sistema. Autenticação verifica uma ou mais evidências apresentadas por ela; autorização decide quais ações essa identidade pode executar. Uma autenticação bem-sucedida não concede automaticamente acesso a todos os dados ou recursos. O controle por recurso e ação é aprofundado em 20.3.

Defina primeiro o fluxo: quem verifica a credencial, quem cria o estado autenticado, como as requisições seguintes provam que pertencem àquela sessão e quando esse estado deixa de valer. Um login com senha pode autenticar diretamente na aplicação; um provedor externo pode verificar identidade por OpenID Connect. Em ambos os casos, a aplicação ainda precisa estabelecer e proteger a sessão que usa.

**Exemplo:** após autenticar um usuário por OIDC, a aplicação pode criar sua própria sessão local. Isso não significa que o ID Token seja uma autorização irrestrita para qualquer API.

**Erro comum:** tratar login, sessão e autorização como uma única operação, e confiar em um identificador ou papel enviado pelo cliente.

**Checagem:** o que o sistema já sabe após autenticar e o que ainda precisa verificar antes de permitir uma ação? A identidade pode estar verificada; a autorização depende do recurso e da ação.

## Microtópico 2 — Sessão no servidor
Na abordagem tradicional, o servidor mantém o estado da sessão e o navegador recebe um identificador opaco, normalmente enviado em cookie. O identificador deve ser imprevisível e não deve carregar dados pessoais ou privilégios legíveis. Configure atributos de cookie adequados à arquitetura, como Secure e HttpOnly; escolha SameSite e domínio/escopo de forma consciente.

Renove o identificador ao autenticar ou elevar privilégio para evitar session fixation. No logout, invalide a sessão no servidor e limpe o cookie. Apagar apenas o cookie do navegador não invalida uma cópia roubada. Defina expiração por inatividade e/ou limite absoluto conforme o risco; fechar o navegador não é controle de encerramento confiável.

Cookies são enviados automaticamente pelo navegador. Portanto, uma sessão baseada em cookie exige avaliação de CSRF. HttpOnly dificulta que JavaScript leia o valor do cookie, mas não impede que script malicioso faça ações em nome da página e não corrige XSS.

**Exemplo:** o navegador envia um cookie de sessão ao backend; o backend consulta o estado correspondente e verifica se a sessão continua ativa. Uma sessão distribuída pode exigir armazenamento compartilhado ou mecanismo que mantenha a invalidação consistente entre instâncias.

**Erro comum:** supor que usar cookie seguro resolve todos os riscos, ou que apagar o cookie encerra a sessão do lado do servidor.

**Checagem:** após o logout, uma cópia antiga do identificador ainda funciona? O servidor deve recusá-la.

## Microtópico 5 — Renovação, expiração e encerramento
Access tokens curtos reduzem a janela de uso se vazarem, mas exigem estratégia de renovação. Refresh tokens permitem solicitar novos access tokens e, por isso, são credenciais de alto valor. Em clientes públicos, a orientação atual exige refresh tokens com rotação em cada uso ou vínculo criptográfico ao cliente; também requer limite de vida ou expiração por inatividade. Se houver reutilização de um refresh token invalidado, a detecção deve permitir responder ao possível replay segundo a política do provedor.

Revogar um refresh token impede renovações futuras, mas não necessariamente torna um access token já emitido imediatamente inválido em toda API. Logout deve corresponder ao estado que o produto pretende encerrar: sessão local, credencial de renovação, sessão do provedor de identidade ou uma combinação. Não prometa logout global se somente o cookie local foi invalidado.

Planeje também expiração, logout em outros dispositivos e resposta a eventos como troca de senha ou comprometimento. Senhas, armazenamento de hashes, recuperação de conta e MFA são aprofundados em 20.2; não armazene senha em texto puro nem implemente protocolo de autenticação criptográfica por conta própria.

**Exemplo:** o servidor encerra a sessão local e revoga ou invalida a cadeia de refresh tokens suportada pelo provedor; access tokens já distribuídos podem continuar aceitos até expirarem, dependendo da API e do mecanismo de revogação.

**Erro comum:** dizer “logout revoga tudo” sem identificar quais estados ou credenciais são realmente invalidados.

**Checagem:** que artefatos continuam válidos depois do logout e por quanto tempo? Responda separadamente para sessão local, refresh token, access token e sessão do provedor.

