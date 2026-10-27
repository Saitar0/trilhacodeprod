---
arquivo_id: "f3-6-2-90-integracao-p03-pratica-transferencia-relatorio-tarefas"
parent_key: "6.2"
tipo_arquivo: "practice"
assuntos: ["01_funcoes_retorno_responsabilidade", "02_arrays_objetos_colecoes", "03_escopo_fluxo_dados", "04_transformacao_mutacao"]
ordem: 3
itens_origem: ["P3"]
---

### 3. Transferência — relatório de tarefas
Crie uma lista de objetos `{ id, titulo, ativa, prioridade }`. Escreva funções separadas para filtrar tarefas ativas, ordenar por prioridade crescente e calcular quantas estão ativas. Cada função deve receber os dados por parâmetro. As funções de filtro e ordenação devolvem resultados; não altere a lista original. Teste lista vazia e prioridades iguais.

**Entregue:** dados de entrada, três funções, resultado esperado para uma lista de pelo menos quatro tarefas, estado da lista original antes/depois e testes com `[]` e prioridades iguais. Na ordenação, use um comparador numérico e uma cópia rasa antes de `sort()`.

**Dicas graduais:** (1) `filter()` seleciona sem reorganizar a lista recebida; (2) `sort()` muta, então copie antes; (3) um contador pode ser implementado com laço e retornar zero para uma coleção vazia.

