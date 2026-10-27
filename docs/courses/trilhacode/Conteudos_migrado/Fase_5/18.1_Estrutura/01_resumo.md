---
arquivo_id: "f5-18-1-01-resumo"
parent_key: "18.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Modele caminhos em torno de recursos e respeite a semântica dos métodos HTTP.
- Semântica idempotente facilita repetição segura, mas precisa ser cumprida pela implementação.
- Middlewares tratam preocupações transversais; controllers conectam HTTP à aplicação; serviços aplicam regras.
- Valide em runtime toda entrada externa; tipos estáticos não validam requisições.
- Status e formato de erro fazem parte do contrato; não exponha detalhes internos.

