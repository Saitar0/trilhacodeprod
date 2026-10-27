---
arquivo_id: "f4-12-1-90-integracao-p02-pratica"
parent_key: "12.1"
tipo_arquivo: "practice"
assuntos: ["01_hipoteses_planos_explain_medicao", "02_indices_custo_escrita"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Teste uma hipótese de índice
Na tabela de catálogo, a tela filtra por categoria e mostra os itens recentes. Compare o plano antes e depois de criar um índice de estudo sobre `(categoria_id, criado_em DESC)). Use dados representativos e considere que criar índice modifica o schema do ambiente de prática.

**Tarefas**
1. Registre o plano inicial.
2. Crie o índice candidato e registre novamente o plano e o tempo.
3. Compare resultado e número de linhas para garantir que a consulta continua correta.
4. Explique o custo do índice sobre armazenamento e escritas.
5. Apresente uma conclusão limitada ao ambiente medido.

**Dica:** mantenha consulta, dados e parâmetros iguais; o otimizador pode escolher não usar o índice.

