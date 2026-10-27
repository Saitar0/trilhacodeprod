---
arquivo_id: "f7-32-2-02-criterio-de-conclusao-md"
parent_key: "32.2"
tipo_arquivo: "criterio"
ordem: 0
itens_origem: ["Critério de conclusão"]
---

## Critério de conclusão
O pipeline constrói um artefato rastreável uma vez e o implanta em staging isolado. Um smoke check pós-deploy bloqueia avanço quando falha; a pessoa demonstra rollback da aplicação para versão conhecida e explica, com uma sequência de migração, por que dados e schema exigem tratamento próprio. Evidências distinguem o que foi executado do que foi apenas planejado.

