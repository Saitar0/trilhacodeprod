---
arquivo_id: "f4-12-2-90-integracao-p01-pratica"
parent_key: "12.2"
tipo_arquivo: "practice"
assuntos: ["01_transacoes_isolamento_concorrencia", "02_locks_conflitos_otimistas_pessimistas"]
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### Atividade 1 — Impeça saldo negativo sob concorrência
Em um banco de estudo, produto id 42 tem estoque 1. Em duas sessões, tente reservar uma unidade quase ao mesmo tempo. Compare uma implementação ingênua (SELECT seguido de UPDATE sem proteção) com uma atualização condicional atômica.

**Tarefas**
1. Execute a atualização condicional para reservar uma unidade.
2. Repita a tentativa em uma segunda sessão.
3. Verifique que apenas uma tentativa altera uma linha e o estoque nunca fica negativo.
4. Explique como distinguir produto inexistente de saldo insuficiente se a regra exigir mensagens diferentes.

**Dica:** verifique o número de linhas retornadas pelo UPDATE ... RETURNING; não use somente uma decisão feita antes da atualização.

