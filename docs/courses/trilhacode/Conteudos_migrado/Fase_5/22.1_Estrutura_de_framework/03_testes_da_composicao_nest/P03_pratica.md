---
arquivo_id: "f5-22-1-03-testes-da-composicao-nest-p03-pratica"
parent_key: "22.1"
tipo_arquivo: "practice"
assunto: "03_testes_da_composicao_nest"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Teste a fronteira com TestingModule
**Objetivo:** confirmar comportamento do provider e resolução da dependência sem substituir o sistema inteiro por mocks.

**Passos:**
1. Crie um TestingModule para o provider escolhido com seus metadados/dependências essenciais.
2. Substitua o token de uma integração externa por uma implementação em memória ou stub que responda aos casos necessários.
3. Teste um resultado esperado e uma falha de dependência/regra.
4. Crie ou descreva um teste de integração de módulo que use o registro real para confirmar a associação provider-token.
5. Explique quais garantias cada teste oferece e quais não oferece.

**Dica:** o teste isolado pode validar regra sem provar que o módulo de produção registra a implementação corretamente. Use um teste de integração para essa pergunta.

