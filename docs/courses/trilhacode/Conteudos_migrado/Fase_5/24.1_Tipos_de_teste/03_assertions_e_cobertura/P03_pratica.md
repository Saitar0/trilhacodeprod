---
arquivo_id: "f5-24-1-03-assertions-e-cobertura-p03-pratica"
parent_key: "24.1"
tipo_arquivo: "practice"
assunto: "03_assertions_e_cobertura"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Revise cobertura contra comportamento

**Desafio:** uma função aplica desconto quando o cliente é ativo e o valor supera o mínimo. O relatório indica linha executada, mas os testes só verificam um cliente ativo acima do mínimo.

**Passos:**
1. Enumere as decisões e limites: cliente ativo/inativo e valor abaixo, igual e acima do mínimo.
2. Escreva tabela de casos com resultado esperado, incluindo arredondamento ou zero se o contrato exigir.
3. Identifique qual branch não foi exercitado e qual asserção confirma cada resultado.
4. Proponha uma mutação simples, como remover a verificação de cliente ativo, e diga qual teste deve falhar.
5. Separe o que essa cobertura local prova do que precisaria de integração.

**Dica:** um ramo pode ser executado parcialmente sem verificar todos os resultados relevantes.

