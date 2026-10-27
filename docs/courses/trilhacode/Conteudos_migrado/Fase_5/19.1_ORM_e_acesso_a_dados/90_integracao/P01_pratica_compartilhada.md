---
arquivo_id: "f5-19-1-90-integracao-p01-pratica-compartilhada"
parent_key: "19.1"
tipo_arquivo: "practice"
assuntos: ["01_mapeamento_orm_responsabilidades", "04_migrations_sql_explicito"]
ordem: 1
itens_origem: ["P1"]
---

## Atividades práticas

### Atividade 1 — Modelagem e migration
**Objetivo:** mapear duas entidades relacionadas e produzir uma evolução reproduzível do schema.

**Passos:**
1. Escolha duas entidades do projeto com relação clara, como Cliente e Pedido.
2. Defina campos obrigatórios, chave primária, chave estrangeira e uma regra de unicidade ou índice justificada.
3. Implemente o mapeamento no ORM escolhido e gere/escreva a migration.
4. Revise o DDL antes de aplicar; aplique em banco de desenvolvimento e confirme as constraints.
5. Explique como uma base vazia recebe essa mudança pelo histórico de migrations.

**Dica:** descreva primeiro as invariantes do domínio. Não dependa apenas de validações no formulário ou serviço.

