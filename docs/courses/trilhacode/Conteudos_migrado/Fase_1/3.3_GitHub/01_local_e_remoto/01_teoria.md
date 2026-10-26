---
arquivo_id: "f1-3-3-01-local-e-remoto-01-teoria"
parent_key: "3.3"
tipo_arquivo: "theory"
assunto: "01_local_e_remoto"
ordem: 1
itens_origem: ["Local e remoto"]
---

## Teoria

### Local e remoto
Um repositório **local** está no seu computador; um **remoto** é uma cópia hospedada em outro lugar, como GitHub. `git clone` cria uma cópia local de um remoto e configura uma referência chamada normalmente `origin`. `git fetch` busca objetos e referências novas sem integrar automaticamente as mudanças à sua branch. `git pull` busca e integra alterações (por padrão, em geral por merge; a configuração pode mudar esse comportamento). `git push` envia commits locais para o remoto, se as permissões e regras permitirem.

Antes de sincronizar, confira branch e estado. Se o remoto rejeitar um push por ter commits novos, busque as mudanças, integre-as conscientemente e tente novamente. Não use force push como atalho em branch compartilhada.

