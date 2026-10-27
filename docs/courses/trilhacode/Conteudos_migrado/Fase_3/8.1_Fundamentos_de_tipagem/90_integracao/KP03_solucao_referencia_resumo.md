---
arquivo_id: "f3-8-1-90-integracao-kp03-solucao-referencia-resumo"
parent_key: "8.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_tipos_primitivos_anotacoes", "02_unions_narrowing", "03_inferencia_contratos_forma_objetos"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** `StatusTarefa` é a union literal já proposta; `FiltroTarefas` pode ser `"todas" | "abertas" | "concluidas"`; `ResumoTarefas` pode ser uma interface com `total: number`, `concluidas: number` e `titulosAbertas: string[]`. A função usa `length` para contar a lista e `filter` para obter tarefas concluídas ou abertas. Para entrada vazia, as contagens e a lista resultam em zero e `[]`. O identificador é tratado com `typeof` antes de uma operação específica. São válidas implementações equivalentes que não mutem a entrada e atendam aos contratos.

