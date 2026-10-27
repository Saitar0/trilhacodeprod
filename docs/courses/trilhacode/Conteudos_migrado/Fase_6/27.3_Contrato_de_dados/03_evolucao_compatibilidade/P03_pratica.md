---
arquivo_id: "f6-27-3-03-evolucao-compatibilidade-p03-pratica-md"
parent_key: "27.3"
tipo_arquivo: "practice"
assunto: "03_evolucao_compatibilidade"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Revisar evolução e compatibilidade de contrato
**Contexto e objetivo:** detectar mudança que quebra consumidores e planejar uma migração compatível.

**Situação:** versão atual usa `{ "id": "t-17", "title": "Revisar", "dueDate": null }`. A proposta quer remover `title`, trocar `dueDate` para Unix timestamp numérico e adicionar `status`.

**Instruções:** classifique cada mudança como potencialmente compatível ou incompatível e justifique; escreva uma alternativa de migração que mantenha cliente antigo funcional por um período; proponha exemplos/testes para contrato antigo e novo; defina como saber quando o campo antigo pode ser removido. Considere consumidor estrito que rejeita propriedades desconhecidas.

**Entrega:** matriz “mudança → consumidor afetado → risco → plano de migração” e conjunto mínimo de exemplos/testes de contrato.

**Dica gradual:** adicionar `status` opcional pode ser aditivo para muitos consumidores; remover `title` e alterar o tipo de `dueDate` mudam contrato existente. Uma transição pode adicionar campo novo antes de descontinuar o antigo.

**Feedback e erro comum:** o plano mantém compatibilidade durante transição, nomeia os consumidores e define evidência de uso/depreciação. Erro comum: chamar toda adição de campo de segura sem verificar validação estrita ou tipos gerados.

