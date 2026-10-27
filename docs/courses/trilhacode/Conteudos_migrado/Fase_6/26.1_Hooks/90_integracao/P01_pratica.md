---
arquivo_id: "f6-26-1-90-integracao-p01-pratica-md"
parent_key: "26.1"
tipo_arquivo: "practice"
assuntos: ["01_regras_de_chamada", "02_effects_sincronizacao_limpeza", "03_refs_valores_imperativos", "04_memoizacao_decisao_por_evidencia"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Audite e reorganize a chamada de Hooks

**Desafio:** corrija um componente que chama useEffect dentro de uma condição, useRef para armazenar o texto visível e usa useMemo para todo valor calculado.

**Passos:**
1. Identifique quais dados precisam renderizar a interface e quais são apenas imperativos.
2. Mova todos os Hooks ao topo do componente antes de retornos condicionais.
3. Use estado para o texto que aparece na tela e mantenha a ref apenas se houver uma necessidade imperativa, como foco.
4. Remova Effect que só copia um valor derivado e calcule esse valor durante a renderização.
5. Explique por que cada Hook restante é apropriado.

**Dica:** não basta mover o Hook de lugar se o trabalho dentro dele continuar sem necessidade.

