---
arquivo_id: "f6-27-1-02-autenticacao-credenciais-01-teoria-md"
parent_key: "27.1"
tipo_arquivo: "theory"
assunto: "02_autenticacao_credenciais"
ordem: 2
itens_origem: ["## Microtópico 2 — Autenticação e credenciais exigem decisão explícita"]
---

## Microtópico 2 — Autenticação e credenciais exigem decisão explícita

Quando o contrato usar bearer token, envie-o no header Authorization: Bearer, nunca na URL. URLs podem aparecer em histórico, logs, métricas, captura de tela e Referer. Não exponha segredos de servidor no bundle do frontend: qualquer valor enviado ao navegador pode ser inspecionado por quem o utiliza.

Escolha de armazenamento depende do desenho de sessão e da ameaça:
- Manter um access token apenas em memória reduz persistência após recarga, mas a aplicação precisa lidar novamente com a sessão ao recarregar.
- localStorage é acessível a qualquer JavaScript executado na origem; uma falha XSS pode ler tokens. Não o trate como cofre para credenciais sensíveis.
- Cookie HttpOnly impede leitura direta pelo JavaScript da página, mas o navegador envia cookies automaticamente. Operações autenticadas por cookie precisam de defesa contra CSRF, configuração Secure/SameSite adequada ao fluxo e validação no servidor.

Não há uma escolha universal que o frontend possa tomar sem o backend. Siga o contrato da aplicação e documente o compromisso entre XSS, CSRF, persistência e experiência. Um bearer token no header criado por JavaScript não é enviado automaticamente pelo navegador como cookie, mas ainda pode ser roubado se o código da origem for comprometido.

Trate 401 como não autenticado ou credencial expirada conforme o contrato; 403 significa que a identidade não tem permissão para a operação. Não faça refresh ou novo login em loop para qualquer erro: limite tentativas, proteja ações não idempotentes e encerre/renove a sessão segundo política definida.

