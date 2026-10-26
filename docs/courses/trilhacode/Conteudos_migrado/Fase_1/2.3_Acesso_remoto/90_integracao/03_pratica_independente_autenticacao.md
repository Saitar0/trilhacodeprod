---
arquivo_id: "f1-2-3-90-integracao-03-pratica-independente-autenticacao"
parent_key: "2.3"
tipo_arquivo: "practice"
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — diagnostique uma falha de autenticação

Uma pessoa informa que a conexão SSH falhou com `Permission denied (publickey)`. Ela afirma que cadastrou “a chave”, mas não sabe dizer qual arquivo. O repositório pode estar configurado com URL SSH ou HTTPS.

**Entregue:** uma sequência de até seis verificações, em ordem, que ajude a localizar o problema. Para cada etapa, diga que resultado observar e qual hipótese ele ajuda a avaliar. Inclua como confirmar o tipo de URL remota e como testar a autenticação. Não peça nem exponha a chave privada ou a passphrase.

**Dicas progressivas**

- Primeiro confirme se o repositório realmente usa SSH. Uma URL HTTPS segue outro fluxo e não depende dessa chave SSH.
- A mensagem de falha é compatível com várias causas: chave pública ausente ou diferente da privada oferecida, chave não carregada/selecionada, conta errada ou configuração do cliente. Avance por evidências, sem desativar a verificação do servidor.

