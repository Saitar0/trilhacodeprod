---
arquivo_id: "f4-11-3-90-integracao-p02-pratica"
parent_key: "11.3"
tipo_arquivo: "practice"
assuntos: ["02_psql_scripts_metacomandos", "03_ddl_dml_com_cuidado"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Recrie esquema e dados de demonstração
Crie um arquivo `scripts/01_schema.sql) para tabela cliente e pedido. Cliente tem id e nome; Pedido tem id, cliente_id, status e total, com referência ao cliente e total não negativo. Insira duas linhas de cliente e três pedidos e registre o processo em um segundo script.

**Tarefas**
1. Separe o DDL do script de dados iniciais.
2. Execute os scripts no banco de estudo.
3. Use `\dt), `\d pedido) e SELECT para conferir estrutura e dados.
4. Explique por que esses scripts não substituem backup.

**Dica:** use a ordem de dependência: primeiro cliente, depois pedido.

