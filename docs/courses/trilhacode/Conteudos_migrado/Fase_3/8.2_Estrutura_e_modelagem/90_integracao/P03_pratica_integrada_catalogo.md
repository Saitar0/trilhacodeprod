---
arquivo_id: "f3-8-2-90-integracao-p03-pratica-integrada-catalogo"
parent_key: "8.2"
tipo_arquivo: "practice"
assuntos: ["01_formas_dados_unions", "02_generics_composicao_contratos", "03_unknown_validacao_runtime"]
ordem: 3
itens_origem: ["P3"]
---

### 3. Integrada — valide resposta de catálogo
Receba um valor `unknown` de fonte externa, valide se ele representa um produto e devolva `Resultado<Produto>`. Inclua três casos: produto válido, preço com tipo incorreto e `null`. Depois use `primeiro<T>` com uma coleção e explique o tipo retornado quando ela está vazia.

**Dica:** crie uma guarda `ehProduto(valor): valor is Produto` e use-a antes de montar o resultado discriminado.

