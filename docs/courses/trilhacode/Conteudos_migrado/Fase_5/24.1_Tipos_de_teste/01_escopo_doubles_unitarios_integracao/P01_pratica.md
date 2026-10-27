---
arquivo_id: "f5-24-1-01-escopo-doubles-unitarios-integracao-p01-pratica"
parent_key: "24.1"
tipo_arquivo: "practice"
assunto: "01_escopo_doubles_unitarios_integracao"
ordem: 1
itens_origem: ["P1"]
---

## Atividades práticas

### Atividade 1 — Monte uma matriz de confiança para pedidos

**Desafio:** um fluxo recebe pedido HTTP, verifica limite de crédito, salva pedido no PostgreSQL e publica um evento. Planeje testes que cubram os riscos sem duplicar tudo em E2E.

**Passos:**
1. Liste pelo menos cinco riscos: regra de crédito, campos inválidos, constraint/transação, falha de publicação e resposta HTTP.
2. Para cada risco, escolha escopo, componentes reais, dublês e resultado a afirmar.
3. Identifique um caso de falha que não deve persistir pedido e outro que precisa comprovar a constraint real.
4. Escolha um fluxo E2E principal e diga quais verificações ele fornece.
5. Registre um risco que continua fora da suíte proposta.

**Dica:** “mockar o banco” e “testar o banco” respondem a perguntas diferentes.

