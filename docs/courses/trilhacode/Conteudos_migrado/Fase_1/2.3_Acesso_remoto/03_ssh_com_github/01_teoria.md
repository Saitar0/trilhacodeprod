---
arquivo_id: "f1-2-3-03-ssh-com-github-01-teoria"
parent_key: "2.3"
tipo_arquivo: "theory"
assunto: "03_ssh_com_github"
ordem: 3
itens_origem: ["Usar SSH com GitHub"]
---

### Usar SSH com GitHub
Para usar SSH com GitHub, gere ou escolha uma chave compatível, adicione somente a chave pública à conta e teste a autenticação. O endereço remoto do repositório deve usar o formato SSH, por exemplo `git@github.com:organizacao/repositorio.git`; um endereço HTTPS usa outro método de autenticação. A chave de conta não deve ser confundida com uma deploy key associada a um repositório específico.

Antes de aceitar a identidade de um servidor, verifique a impressão digital por um canal confiável, sobretudo na primeira conexão. A confirmação salva uma chave de host conhecida; se ela mudar inesperadamente, pare e investigue em vez de ignorar o aviso.

