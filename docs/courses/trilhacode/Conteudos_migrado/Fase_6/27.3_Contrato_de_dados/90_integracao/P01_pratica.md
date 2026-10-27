---
arquivo_id: "f6-27-3-90-integracao-p01-pratica-md"
parent_key: "27.3"
tipo_arquivo: "practice"
assuntos: ["01_fronteira_contrato_validacao_runtime", "02_presenca_nulidade_variacoes"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Especificar contrato de uma listagem paginada
**Contexto e objetivo:** transformar um exemplo de endpoint em contrato verificável para cliente e API.

**Dados iniciais:** endpoint `GET /api/tasks?page=1&pageSize=20`, resposta de exemplo:

```json
{
  "items": [{ "id": "t-17", "title": "Revisar contrato", "dueDate": null }],
  "page": 1,
  "pageSize": 20,
  "total": 1
}
```

**Instruções:** escreva os tipos TS e descreva o contrato HTTP: parâmetros e limites, campos obrigatórios/opcionais/anuláveis, caso sem resultados, comportamento para parâmetro inválido, status e formato de erro. Inclua um exemplo de resposta válida vazia e um exemplo de falha de validação. Não escolha limites silenciosamente: anote-os como decisões do contrato.

**Entrega:** definição TS, rascunho OpenAPI ou tabela de contrato com exemplos válidos e inválidos.

**Dica gradual:** determine primeiro se cada propriedade pode faltar, ser nula ou ambas as coisas. Depois defina faixa de `pageSize` e resposta para página fora da faixa.

**Feedback e erro comum:** a descrição precisa distinguir `items: []` de ausência de `items` e `dueDate: null` de campo omitido. Erro comum: usar um único formato de resposta para sucesso e erro sem definir status HTTP ou semântica.

