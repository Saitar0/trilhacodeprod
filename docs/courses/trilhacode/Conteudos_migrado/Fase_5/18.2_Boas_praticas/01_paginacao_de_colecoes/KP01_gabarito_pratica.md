---
arquivo_id: "f5-18-2-01-paginacao-de-colecoes-kp01-gabarito-pratica"
parent_key: "18.2"
tipo_arquivo: "answer_key_pratica"
assunto: "01_paginacao_de_colecoes"
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:** uma resposta contém items e nextCursor opcional; parâmetros incluem pageSize com limite, filtros e cursor; ordem usa data mais ID. Se o cursor estiver ausente, começa do início; se não houver próximos itens, nextCursor é omitido ou nulo conforme o contrato. A API documenta se filtros/ordenação são associados ao cursor e admite que o conjunto pode mudar sem oferecer snapshot. Offset pode bastar em coleção pequena e estável; cursor é preferível para percorrer listas grandes e mutáveis.

