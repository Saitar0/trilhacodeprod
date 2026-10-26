---
arquivo_id: "f1-2-2-01-usuarios-e-permissoes-01-teoria"
parent_key: "2.2"
tipo_arquivo: "theory"
assunto: "01_usuarios_e_permissoes"
ordem: 1
itens_origem: ["Usuários e permissões"]
---

## Teoria

### Usuários e permissões
O sistema operacional associa ações a identidades e permissões. Em sistemas Unix, cada arquivo tem proprietário, grupo e permissões para proprietário, grupo e demais usuários. `r` permite ler; `w`, modificar; `x` permite executar um arquivo ou atravessar um diretório. Para diretórios, `x` significa poder acessar nomes dentro dele; leitura permite listar nomes, sujeito também às demais permissões.

`chmod` altera permissões; `chown` altera proprietário/grupo e normalmente requer privilégios apropriados. Não use `sudo` automaticamente nem “resolva” todo erro concedendo acesso amplo. Primeiro descubra qual recurso está sendo acessado, com qual usuário e qual permissão realmente falta. A forma de permissões também difere no Windows, que usa ACLs e outras regras.

