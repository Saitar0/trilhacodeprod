---
arquivo_id: "f4-9-3-90-integracao-p03-pratica"
parent_key: "9.3"
tipo_arquivo: "practice"
assuntos: ["02_integridade_referencial_e_exclusao", "03_limites_constraints_e_evolucao_segura"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Investigue uma regra entre linhas
Um sistema registra empréstimos com exemplar_id, inicio e fim. Um exemplar não pode estar em dois empréstimos ativos ao mesmo tempo. O histórico de empréstimos encerrados deve ser mantido.

**Tarefas**
1. Explique por que `CHECK (fim IS NULL)` não expressa a exclusividade entre empréstimos.
2. Declare a regra de domínio com precisão, incluindo o significado de “ativo”.
3. Proponha um mecanismo adequado para o PostgreSQL ou descreva uma estratégia transacional segura.
4. Mostre dois casos que devem ser aceitos e um conflito que deve ser rejeitado.

**Dica:** a regra compara períodos ou estados de linhas distintas; não faça uma UNIQUE simples em exemplar_id que bloqueie o histórico inteiro.

