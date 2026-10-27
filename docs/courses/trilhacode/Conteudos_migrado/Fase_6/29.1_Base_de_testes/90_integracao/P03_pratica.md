---
arquivo_id: "f6-29-1-90-integracao-p03-pratica-md"
parent_key: "29.1"
tipo_arquivo: "practice"
assuntos: ["02_runner_ambiente", "04_isolamento_assertions"]
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Revise isolamento, mocks e valor das assertions
**Objetivo:** identificar uma suíte frágil e torná-la capaz de detectar uma regressão plausível.

**Passos:**
1. Selecione um teste existente que use muitas classes internas, snapshot amplo ou mock de comportamento central.
2. Escreva em linguagem simples qual contrato do componente o teste deveria garantir.
3. Substitua dependências externas por respostas controladas, mantendo intacto o componente e a regra sob teste.
4. Garanta que dados, mocks e estado sejam preparados e limpos por caso, sem depender de outra execução.
5. Introduza uma alteração temporária plausível, como esconder uma mensagem ou ignorar um filtro, e confirme que a assertion relevante falha; depois restaure o comportamento.

**Dica:** um teste pode afirmar chamadas de função como evidência auxiliar, mas deve verificar também o resultado visível quando esse resultado é o contrato.

**Entrega:** teste revisado, descrição do defeito simulado e breve justificativa do limite do mock.

**Critérios de conclusão:** o teste não depende de detalhes internos frágeis; controla somente a dependência necessária; detecta a regressão simulada e roda isoladamente.

