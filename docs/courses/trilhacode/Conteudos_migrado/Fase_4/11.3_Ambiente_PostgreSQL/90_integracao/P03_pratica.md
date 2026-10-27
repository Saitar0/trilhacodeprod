---
arquivo_id: "f4-11-3-90-integracao-p03-pratica"
parent_key: "11.3"
tipo_arquivo: "practice"
assuntos: ["03_ddl_dml_com_cuidado", "04_confirmacao_reversao_dml"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Atualize com confirmação e reversão
Na tabela de pedidos de estudo, altere o status de um pedido identificado pelo id. Primeiro confira o alvo, depois teste a alteração em uma transação e decida se confirma ou desfaz.

**Tarefas**
1. Consulte o pedido pelo id e confirme a linha esperada.
2. Execute UPDATE com WHERE e RETURNING dentro de BEGIN.
3. Confira a alteração antes de decidir.
4. Use ROLLBACK para ensaiar ou COMMIT para persistir.
5. Explique o efeito de remover WHERE.

**Dica:** faça primeiro SELECT com o mesmo WHERE, e confirme se o id existe no banco certo.

