---
arquivo_id: "f5-18-2-01-paginacao-de-colecoes-01-teoria"
parent_key: "18.2"
tipo_arquivo: "theory"
assunto: "01_paginacao_de_colecoes"
ordem: 1
itens_origem: ["theory-container", "1. Paginação para coleções"]
---

## Teoria

### 1. Paginação para coleções
Uma rota que lista uma coleção deve limitar o tamanho da resposta desde o início. Defina tamanho padrão e máximo no servidor, valide valores inválidos e documente o formato da resposta, por exemplo items e nextCursor. Offset/limit é fácil de entender, mas inserções e remoções antes do offset podem deslocar itens entre páginas. Para listas grandes ou que mudam com frequência, paginação por cursor/keyset continua a partir de uma ordenação estável e costuma evitar percorrer e descartar muitas linhas.

A ordenação precisa incluir um desempate único, como data de criação mais ID; sem isso, itens empatados podem reaparecer ou sumir entre páginas. Um cursor opaco deve representar somente a posição de continuação e, quando necessário, os filtros/ordenação usados. A autorização ainda deve ser conferida em cada requisição: cursor não é credencial. Mudanças no conjunto durante a navegação ainda podem alterar os resultados; cursor sozinho não garante uma fotografia transacional. [Google AIP-158 — Pagination](https://google.aip.dev/158).

