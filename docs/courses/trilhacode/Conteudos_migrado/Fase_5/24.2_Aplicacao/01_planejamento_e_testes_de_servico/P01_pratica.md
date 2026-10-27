---
arquivo_id: "f5-24-2-01-planejamento-e-testes-de-servico-p01-pratica"
parent_key: "24.2"
tipo_arquivo: "practice"
assunto: "01_planejamento_e_testes_de_servico"
ordem: 1
itens_origem: ["P1"]
---

## Atividades práticas

### Atividade 1 — Cubra serviço e falhas controladas

**Desafio:** teste o serviço de criação de pedido com repositório e gateway de crédito substituídos.

**Passos:**
1. Defina entradas válidas, inválidas e acima do limite de crédito.
2. Programe o dublê do gateway para aprovar, rejeitar e falhar por indisponibilidade.
3. Para cada caso, afirme resultado/erro de negócio e se o serviço pediu persistência quando devia.
4. Confirme que pedido inválido ou rejeitado não é gravado; não verifique interações internas sem relação com o contrato.
5. Anote o que esse teste não sabe sobre o banco.

**Dica:** o caso de crédito rejeitado e o caso do gateway indisponível podem exigir respostas diferentes.

