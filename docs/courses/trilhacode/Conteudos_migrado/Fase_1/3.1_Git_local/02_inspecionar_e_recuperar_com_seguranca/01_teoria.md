---
arquivo_id: "f1-3-1-02-inspecionar-e-recuperar-com-seguranca-01-teoria"
parent_key: "3.1"
tipo_arquivo: "theory"
assunto: "02_inspecionar_e_recuperar_com_seguranca"
ordem: 2
itens_origem: ["Inspecionar o histórico", "Branches", "Desfazer com intenção"]
---

### Inspecionar o histórico
`git log` mostra commits; opções como `--oneline --graph --decorate` ajudam a visualizar o histórico. `git show` apresenta um commit e suas alterações. `git diff` compara estados: sem opções, costuma mostrar mudanças ainda fora do staging; `git diff --staged` mostra o que está preparado para o commit.

### Branches
Uma branch é uma referência móvel para uma linha de desenvolvimento; criar uma branch não duplica todo o projeto. Ela permite experimentar mudanças separadas. Confira a branch atual com `git branch --show-current`, crie uma com `git switch -c nome` e alterne com `git switch nome`. Termine um trabalho integrando-o por merge ou pelo fluxo definido no projeto.

### Desfazer com intenção
`git restore arquivo` pode descartar alterações locais daquele arquivo; isso pode apagar trabalho não salvo em commit. `git restore --staged arquivo` tira o arquivo do staging sem necessariamente apagar as alterações da working tree. `git reset` altera o estado do índice e, em certas formas, também referências; `git reset --hard` pode descartar mudanças e não deve ser usado como tentativa genérica de corrigir problemas. Antes de desfazer, execute `git status` e `git diff`; se estiver em dúvida, faça uma cópia ou salve o trabalho em uma branch/commit.

