---
arquivo_id: "f4-9-2-90-integracao-p02-pratica"
parent_key: "9.2"
tipo_arquivo: "practice"
assuntos: ["01_regras_dominio_entidades_chaves", "02_cardinalidade_opcionalidade"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Modelo de biblioteca
Uma biblioteca cadastra leitores, títulos, exemplares físicos e empréstimos. Um título pode ter vários exemplares; cada exemplar corresponde a um título. Um leitor pode fazer vários empréstimos ao longo do tempo; cada empréstimo pertence a um leitor e registra datas de retirada e devolução. Um empréstimo pode incluir mais de um exemplar, e o mesmo exemplar pode participar de empréstimos diferentes ao longo do tempo, mas não pode estar em dois empréstimos ativos simultaneamente.

**Tarefas**
1. Modele as entidades e chaves principais.
2. Represente empréstimo e exemplar, incluindo a associação necessária.
3. Registre mínimos/máximos e a regra temporal de empréstimo ativo.
4. Indique um atributo que não deve ficar no Título se variar por exemplar.

**Dica:** título bibliográfico não é o mesmo objeto que a cópia física; a regra de “ativo” depende do tempo.

