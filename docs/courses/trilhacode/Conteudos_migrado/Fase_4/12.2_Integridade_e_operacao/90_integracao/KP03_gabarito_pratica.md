---
arquivo_id: "f4-12-2-90-integracao-kp03-gabarito-pratica"
parent_key: "12.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["03_migrations_rollout", "04_backup_restore"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** uma sequência possível é adicionar telefone aceitando NULL; implantar código que lê o campo e grava quando disponível; preencher os registros com dados válidos; conferir contagem de NULLs e qualidade; tornar a coluna obrigatória somente quando todos os dados e versões da aplicação estiverem prontos. O plano pode exigir etapa adicional de transição ou correção; não invente valores para dados desconhecidos sem regra de domínio. Teste dump e restore em outra base/ambiente, verifique schema, contagens e consultas críticas. Migration evolui o schema e/ou dados; backup/restore recupera uma cópia. Remover a coluna ou sobrescrever dados pode tornar rollback destrutivo, então documente a recuperação e preservação.

