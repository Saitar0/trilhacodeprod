---
arquivo_id: "f4-11-3-02-psql-scripts-metacomandos-01-teoria"
parent_key: "11.3"
tipo_arquivo: "theory"
assunto: "02_psql_scripts_metacomandos"
ordem: 2
itens_origem: ["2. Use psql para explorar e executar scripts"]
---

### 2. Use psql para explorar e executar scripts
psql é o cliente de terminal interativo do PostgreSQL. Os comandos com barra invertida são metacomandos do cliente, não SQL enviado ao servidor. Alguns úteis:

- `\conninfo` mostra informações da conexão atual.
- `\l` lista bancos visíveis.
- `\dt` lista tabelas no schema atual.
- `\d nome_tabela` descreve uma tabela.
- `\i caminho/arquivo.sql` executa um arquivo SQL.
- `\q` encerra o cliente.

O SQL termina com ponto e vírgula; uma quebra de linha sozinha não finaliza a instrução. Um script `.sql) versionado torna a criação de tabelas e os dados didáticos reproduzíveis. Para executar arquivo pelo terminal e parar no primeiro erro:

```sh
psql -h localhost -U estudo -d trilha_estudo -v ON_ERROR_STOP=1 -f scripts/01_schema.sql
```

CREATE DATABASE é uma operação administrativa e deve ser executada conectado a outro banco, como `postgres), por um usuário autorizado. Depois, conecte-se ao banco criado para criar tabelas e dados. Não confunda bancos diferentes com schemas do mesmo banco.

**Erro comum:** tentar criar um banco estando conectado a ele ou tratar `\dt) como uma instrução SQL.

