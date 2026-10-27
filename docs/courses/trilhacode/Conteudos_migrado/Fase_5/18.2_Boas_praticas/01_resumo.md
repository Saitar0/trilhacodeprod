---
arquivo_id: "f5-18-2-01-resumo"
parent_key: "18.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Limite coleções no servidor e escolha offset ou cursor segundo escala e padrão de mudança.
- Cursor exige ordenação estável e não substitui autenticação nem garante snapshot.
- Versione alterações incompatíveis; avalie compatibilidade pelo comportamento dos clientes.
- OpenAPI descreve o contrato, mas precisa acompanhar a implementação.
- Idempotência de POST exige persistência, coordenação concorrente e política de retenção, não apenas adicionar um header.

