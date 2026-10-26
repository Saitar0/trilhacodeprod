---
arquivo_id: "f1-3-1-02-inspecionar-e-recuperar-com-seguranca-04-pratica-guiada-estado"
parent_key: "3.1"
tipo_arquivo: "practice"
assunto: "02_inspecionar_e_recuperar_com_seguranca"
ordem: 1
itens_origem: ["P1"]
---

## Prática — três níveis

Faça as atividades em uma pasta temporária e use somente conteúdo fictício. Antes de qualquer operação de recuperação, confira `git status` e os diffs. Não use arquivos de ambiente ou credenciais reais.

### 1. Guiada — interprete o estado do repositório

Considere esta saída de `git status --short`:

```text
 M README.md
M  plano.md
?? rascunho.md
```

No formato curto, a primeira coluna indica o estado no índice (staging) e a segunda indica o estado da working tree.

**Tarefa:** responda o que está preparado para o próximo commit, o que ainda não foi preparado e o que ainda não é rastreado. Depois, imagine que você quer incluir apenas a mudança de `README.md` no próximo commit, mantendo as outras edições. Escreva a sequência de inspeção e preparação.

