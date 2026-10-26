---
arquivo_id: "f1-3-1-02-inspecionar-e-recuperar-com-seguranca-05-gabarito-pratica-guiada"
parent_key: "3.1"
tipo_arquivo: "answer_key_pratica"
assunto: "02_inspecionar_e_recuperar_com_seguranca"
ordem: 1
itens_origem: ["P1"]
---

**Gabarito comentado:** `README.md` tem alteração somente na working tree; `plano.md` tem alteração no índice; `rascunho.md` é não rastreado. Como o commit registra tudo que já está no índice, primeiro inspecione `git diff --staged -- plano.md` e retire essa mudança do staging com `git restore --staged -- plano.md`. Isso mantém a edição na working tree. Em seguida, revise `git diff -- README.md`, prepare somente `README.md` com `git add README.md` e confirme com `git diff --staged`. A saída pode mostrar ` M plano.md`, `M  README.md` e `?? rascunho.md`. Só então faça o commit; arquivos fora do staging ficam de fora.

