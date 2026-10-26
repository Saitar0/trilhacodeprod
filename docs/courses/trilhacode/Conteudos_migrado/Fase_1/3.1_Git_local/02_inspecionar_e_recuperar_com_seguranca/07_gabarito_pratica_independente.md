---
arquivo_id: "f1-3-1-02-inspecionar-e-recuperar-com-seguranca-07-gabarito-pratica-independente"
parent_key: "3.1"
tipo_arquivo: "answer_key_pratica"
assunto: "02_inspecionar_e_recuperar_com_seguranca"
ordem: 2
itens_origem: ["P2"]
---

**Gabarito comentado:** (1) conferir `git status` e `git diff --staged -- arquivo`; usar `git restore --staged -- arquivo` para tirar do índice preservando a edição local. (2) conferir `git diff -- arquivo` e, somente se a edição puder ser perdida, usar `git restore -- arquivo`; essa operação substitui o conteúdo da working tree pelo conteúdo do índice. (3) revogar/rotacionar a credencial imediatamente e seguir o processo de resposta a segredo exposto; `.gitignore` não remove o commit nem desfaz o acesso já ocorrido. A reescrita do histórico precisa considerar clones e colaboradores. (4) não executar ainda: `git reset --hard` pode descartar mudanças no índice e na working tree; primeiro identificar e preservar qualquer trabalho que precise ser mantido.

