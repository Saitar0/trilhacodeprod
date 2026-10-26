---
arquivo_id: "f1-3-2-01-integracao-e-mensagens-commit-01-teoria"
parent_key: "3.2"
tipo_arquivo: "theory"
assunto: "01_integracao_e_mensagens_commit"
ordem: 1
itens_origem: ["Três formas de integrar mudanças", "Mensagens de commit"]
---

## Teoria

### Três formas de integrar mudanças
`git merge outra-branch` incorpora o trabalho da outra branch na branch atual. Dependendo do histórico, Git pode avançar a referência (fast-forward) ou criar um commit de merge com os pais relevantes.

`git rebase base` reaplica commits da branch atual sobre outra base, criando novos commits com novos identificadores. Isso pode deixar a sequência mais linear, mas reescreve o trecho reaplicado. Evite reescrever commits que outras pessoas já usam sem combinar com elas; isso pode exigir sincronização cuidadosa.

`git cherry-pick <commit>` reaplica em outra branch a mudança de um commit escolhido, criando um novo commit. É útil quando você quer selecionar uma mudança específica, sem integrar todo o conjunto da branch.

### Mensagens de commit
Uma mensagem deve ser curta o bastante para resumir a mudança e específica o bastante para distinguir intenção. Uma convenção como Conventional Commits usa tipos (`feat`, `fix`, `docs`, `refactor`) e uma descrição, podendo incluir escopo e notas de mudança incompatível. É uma convenção adotável, não um requisito do Git.

Exemplo: `docs(guia): explicar resolução de conflitos`. Evite mensagens vagas como `ajustes`, `coisas` ou `final`. Se for obrigatório escrever em inglês, mantenha o idioma consistente, mas preserve clareza.

