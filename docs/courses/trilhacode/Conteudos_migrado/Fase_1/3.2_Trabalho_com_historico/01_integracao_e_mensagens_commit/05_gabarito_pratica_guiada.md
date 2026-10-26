---
arquivo_id: "f1-3-2-01-integracao-e-mensagens-commit-05-gabarito-pratica-guiada"
parent_key: "3.2"
tipo_arquivo: "answer_key_pratica"
assunto: "01_integracao_e_mensagens_commit"
ordem: 1
itens_origem: ["P1"]
---

**Gabarito comentado:** (1) `git merge feature` integra o conjunto; como os históricos divergiram, pode criar um commit com os dois pais. (2) Na branch `feature`, `git rebase main` reaplica os commits sobre `B`, criando novos identificadores, por exemplo `C'` e `D'`; faça isso em histórico privado ou com coordenação se já tiver sido compartilhado. (3) `git cherry-pick D` aplica a mudança daquele commit à branch atual e cria um novo commit; o commit original continua na branch de origem. A escolha depende do objetivo e de quem já usa o histórico.

