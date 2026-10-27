---
arquivo_id: "f6-26-1-04-memoizacao-decisao-por-evidencia-p03-pratica-md"
parent_key: "26.1"
tipo_arquivo: "practice"
assunto: "04_memoizacao_decisao_por_evidencia"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Justifique ou retire memoização

**Desafio:** uma lista filtrada fica lenta em um conjunto grande, mas o time também adicionou useCallback em todos os handlers sem medir.

**Passos:**
1. Defina como reproduzir e medir a lentidão com dados representativos.
2. Use o profiler para identificar cálculo ou componente que consome tempo.
3. Aplique useMemo somente ao cálculo caro com dependências completas, se a medição justificar.
4. Para cada useCallback, identifique componente memoizado ou dependência de Hook que precisa de identidade estável.
5. Compare resultado, comportamento e perfil antes/depois; remova otimização que não tenha benefício observável.

**Dica:** primeiro verifique se renderizações repetidas são problema real; criar uma função por render não é, por si só, um defeito.

