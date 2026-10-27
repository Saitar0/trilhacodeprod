---
arquivo_id: "f6-30-1-01-medicao-baseline-memoizacao-p02-pratica-md"
parent_key: "30.1"
tipo_arquivo: "practice"
assunto: "01_medicao_baseline_memoizacao"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Otimize uma renderização ou um cálculo
**Objetivo:** verificar se memoização reduz trabalho sem alterar o comportamento.

**Passos:**
1. Escolha um componente ou cálculo que o perfil identificou como custoso e anote o comportamento esperado.
2. Confira a estabilidade das props, dos objetos e das dependências que chegam ao trecho.
3. Aplique uma única otimização adequada (`memo`, `useMemo` ou `useCallback`) ou confirme que o React Compiler já cobre o caso.
4. Repita a mesma interação e coleta usada no baseline; registre o resultado, inclusive se não houver melhora.
5. Remova a otimização temporariamente e confira que a interface continua correta; avalie se o ganho justifica manter a complexidade.

**Dica:** não adicione dependências omitidas para “fazer memoizar”; corrija a identidade ou o fluxo de dados sem sacrificar atualização correta.

**Entrega:** comparação antes/depois e decisão fundamentada de manter ou descartar a mudança.

**Critérios de conclusão:** resultado funcional é equivalente; comparação usa o mesmo cenário; dependências estão corretas e a decisão considera custo de manutenção.

