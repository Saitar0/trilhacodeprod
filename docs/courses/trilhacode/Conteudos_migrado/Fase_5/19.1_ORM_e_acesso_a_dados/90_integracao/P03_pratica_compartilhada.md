---
arquivo_id: "f5-19-1-90-integracao-p03-pratica-compartilhada"
parent_key: "19.1"
tipo_arquivo: "practice"
assuntos: ["03_transacoes_unidade_negocio", "04_migrations_sql_explicito"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Atomicidade e SQL parametrizado
**Objetivo:** agrupar gravações relacionadas e demonstrar uso seguro de SQL explícito quando necessário.

**Passos:**
1. Escolha um caso com duas gravações dependentes, como criar pedido e itens ou transferir saldo entre contas.
2. Implemente as operações na transação do ORM; provoque uma falha controlada na segunda operação em ambiente local.
3. Verifique que nenhuma gravação parcial permaneceu.
4. Escreva uma consulta explícita simples que a API usada não represente bem, vinculando valores por parâmetros.
5. Compare intenção, resultado e plano/SQL com a alternativa de API do ORM, explicando por que manteria uma delas.

**Dica:** não inclua chamadas de rede na transação. A falha deve ser simulada apenas em dados descartáveis.

