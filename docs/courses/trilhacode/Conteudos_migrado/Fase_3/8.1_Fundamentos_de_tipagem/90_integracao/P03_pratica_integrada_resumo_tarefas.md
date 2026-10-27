---
arquivo_id: "f3-8-1-90-integracao-p03-pratica-integrada-resumo-tarefas"
parent_key: "8.1"
tipo_arquivo: "practice"
assuntos: ["01_tipos_primitivos_anotacoes", "02_unions_narrowing", "03_inferencia_contratos_forma_objetos"]
ordem: 3
itens_origem: ["P3"]
---

### 3. Integrada — tipagem de um resumo de tarefas
Escreva uma função `resumirTarefas(tarefas)` que receba uma lista de tarefas e devolva uma estrutura com:
- quantidade total;
- quantidade concluída;
- títulos das tarefas abertas;
- um rótulo para filtro que aceite `"todas"`, `"abertas"` ou `"concluidas"`.

Defina os contratos com interface e alias, use inferência para variáveis locais quando fizer sentido, e trate uma lista vazia e a descrição ausente. Inclua uma função que recebe um identificador `string | number` e devolve sua representação textual usando narrowing. Não altere a lista de entrada.

**Entregáveis:** tipos nomeados; funções tipadas; exemplos que exercitam lista vazia, campo opcional, status e ambos os formatos de identificador; breve explicação de como o verificador detecta um status inválido.

**Dica:** use `filter` para seleções; compare status com literal; teste o tipo do identificador antes de aplicar uma operação exclusiva.

