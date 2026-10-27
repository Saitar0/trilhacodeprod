---
arquivo_id: "f4-11-3-90-integracao-kp02-gabarito-pratica"
parent_key: "11.3"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_psql_scripts_metacomandos", "03_ddl_dml_com_cuidado"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** crie cliente com PK e nome obrigatório; crie pedido com PK, FK obrigatória para cliente e total com CHECK não negativo. Popule primeiro clientes e depois pedidos. Execute os arquivos com `psql -d trilha_estudo -v ON_ERROR_STOP=1 -f scripts/01_schema.sql) e o arquivo de dados. Scripts reproduzem estrutura e dados conhecidos para o exercício; não preservam automaticamente alterações futuras nem fornecem recuperação de um banco real.

