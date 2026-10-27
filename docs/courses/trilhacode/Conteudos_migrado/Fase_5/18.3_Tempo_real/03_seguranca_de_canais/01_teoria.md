---
arquivo_id: "f5-18-3-03-seguranca-de-canais-01-teoria"
parent_key: "18.3"
tipo_arquivo: "theory"
assunto: "03_seguranca_de_canais"
ordem: 3
itens_origem: ["3. Autenticação, autorização e limites"]
---

### 3. Autenticação, autorização e limites
Autentique a conexão ou o fluxo antes de liberar dados protegidos e autorize cada inscrição em recurso/canal e cada comando recebido. Uma sala organiza destinatários, mas não prova que alguém tem direito de entrar ou executar ações. Revalide expiração e revogação de sessão durante conexões longas; logout pode exigir fechamento imediato dos canais da pessoa.

Para WebSocket no navegador, valide Origin por lista explícita, use WSS em produção e evite credenciais em URLs. Origin ajuda a proteger o handshake, mas não substitui autenticação e autorização. Limite tamanho/frequência das mensagens e conexões para conter abuso. Registre conexões, desconexões, erros de autorização e falhas sem registrar tokens ou conteúdo sensível. [OWASP — WebSocket Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html).

