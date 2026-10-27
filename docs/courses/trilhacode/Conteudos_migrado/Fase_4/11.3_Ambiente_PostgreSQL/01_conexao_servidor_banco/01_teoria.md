---
arquivo_id: "f4-11-3-01-conexao-servidor-banco-01-teoria"
parent_key: "11.3"
tipo_arquivo: "theory"
assunto: "01_conexao_servidor_banco"
ordem: 1
itens_origem: ["1. Entenda servidor, banco, schema e conexão"]
---

## Teoria

### 1. Entenda servidor, banco, schema e conexão
PostgreSQL é um SGBD relacional que implementa SQL e oferece recursos próprios. O servidor pode hospedar vários bancos; dentro de cada banco, schemas organizam tabelas, views, funções e outros objetos. Uma conexão seleciona um servidor e um banco com um usuário autorizado.

Para conectar, identifique host, porta, banco, usuário e método de autenticação. Na instalação local, o host costuma ser `localhost); em Compose, um cliente dentro da mesma rede usa o nome do serviço, como `db), e a porta interna, normalmente 5432. Um cliente no host usa a porta publicada. Uma falha de conexão pode significar servidor parado, host/porta incorretos, banco inexistente ou credenciais/permissões inadequadas.

```sh
psql -h localhost -p 5432 -U estudo -d trilha_estudo
```

O comando pressupõe que o servidor local escuta na porta 5432, que o banco e o usuário existem e que a conexão está autorizada. Não coloque senhas reais diretamente em comandos que possam ficar no histórico ou em logs.

**Erro comum:** tentar resolver todo erro como senha incorreta sem verificar primeiro se o cliente alcança o host e a porta certos.

