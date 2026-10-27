---
arquivo_id: "f3-7-1-01-dom-selecao-01-teoria"
parent_key: "7.1"
tipo_arquivo: "theory"
assunto: "01_dom_selecao"
ordem: 1
itens_origem: ["DOM e seleção de elementos"]
---

## Teoria

### DOM e seleção de elementos
O **DOM** (Document Object Model) representa o documento carregado como uma árvore de nós e objetos. É uma API da plataforma web, não uma parte exclusiva da linguagem JavaScript. O navegador cria essa representação a partir do HTML; scripts podem localizar elementos e atualizar conteúdo, atributos ou estrutura.

`document.querySelector()` localiza o primeiro elemento que corresponde a um seletor CSS. Se nenhum elemento corresponder, retorna `null`; confira o resultado antes de acessar suas propriedades. O seletor precisa ser CSS válido, então um seletor malformado também pode gerar erro.

