---
arquivo_id: "f6-26-1-01-resumo-md"
parent_key: "26.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Chame Hooks no topo de componentes ou custom Hooks, na mesma ordem em todas as renderizações.
- useEffect sincroniza com sistema externo; dependências refletem valores reativos e limpeza desfaz a configuração.
- useRef persiste valor imperativo sem renderizar; use state para dados que precisam alterar a UI.
- useMemo conserva resultado de cálculo; useCallback conserva função; ambos são otimizações com dependências completas.
- Custom Hooks reutilizam lógica, não a mesma instância de estado; React Compiler só deve ser considerado quando configurado no projeto.

