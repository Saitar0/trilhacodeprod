---
arquivo_id: "f4-12-2-90-integracao-p03-pratica"
parent_key: "12.2"
tipo_arquivo: "practice"
assuntos: ["03_migrations_rollout", "04_backup_restore"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Planeje uma migration e comprove recuperação
Uma aplicação precisa adicionar `telefone) obrigatório à tabela cliente, que já contém registros, e uma mudança da aplicação passará a ler e gravar essa coluna. Planeje o rollout e a recuperação sem executar em produção.

**Tarefas**
1. Descreva uma sequência de migrations/implantações compatível com registros antigos e versões antigas da aplicação.
2. Defina verificações antes e depois do backfill.
3. Explique qual caminho de rollback ou correção é possível e que dados podem ser perdidos.
4. Proponha um teste de backup e restore em ambiente isolado.
5. Diferencie o que migration faz do que backup/restore faz.

**Dica:** pense em adicionar a coluna como opcional, implantar código compatível, preencher dados e só então exigir presença; a ordem exata depende do sistema.

