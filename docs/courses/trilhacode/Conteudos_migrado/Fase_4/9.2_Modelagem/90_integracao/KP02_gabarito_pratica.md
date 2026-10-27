---
arquivo_id: "f4-9-2-90-integracao-kp02-gabarito-pratica"
parent_key: "9.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_regras_dominio_entidades_chaves", "02_cardinalidade_opcionalidade"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** Leitor, Título, Exemplar, Empréstimo e ItemEmprestimo. Exemplar tem FK obrigatória para Título; Empréstimo tem FK obrigatória para Leitor; ItemEmprestimo liga Empréstimo e Exemplar. Título participa de 0..N Exemplares e cada Exemplar pertence a 1 Título. Leitor participa de 0..N Empréstimos e cada Empréstimo pertence a 1 Leitor. Empréstimo pode conter 1..N itens conforme a regra de negócio; cada ItemEmprestimo aponta para 1 Empréstimo e 1 Exemplar. Estado de conservação e código de patrimônio pertencem a Exemplar. A regra de empréstimo ativo simultâneo exige considerar intervalos/estado e deve ser implementada por mecanismo de integridade adequado; o modelo conceitual sozinho não garante isso.

