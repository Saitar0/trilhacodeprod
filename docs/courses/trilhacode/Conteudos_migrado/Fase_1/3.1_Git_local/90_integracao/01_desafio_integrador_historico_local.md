---
arquivo_id: "f1-3-1-90-integracao-01-desafio-integrador-historico-local"
parent_key: "3.1"
tipo_arquivo: "practice"
ordem: 3
itens_origem: ["P3"]
---

### 3. Transferência — construa e inspecione um histórico local

Em uma pasta temporária, inicialize um repositório Git e crie `README.md`, `plano.md` e `.gitignore`. Faça um primeiro commit com esses arquivos. Acrescente ao `.gitignore` o caminho `/local.env` e crie `local.env` contendo apenas um valor fictício, como `TOKEN=exemplo-sem-valor-real`; use `git check-ignore -v local.env` para confirmar que o padrão corresponde. Não adicione esse arquivo ao staging.

Anote o nome da branch inicial com `git branch --show-current`. Altere `README.md` e `plano.md` de maneiras diferentes. Use `git status` e `git diff` para preparar apenas `README.md`, inspecione o staging e faça um commit descritivo. Em seguida, registre a alteração de `plano.md` em outro commit. Crie uma branch com `git switch -c pratica/branch`, faça nela uma alteração pequena e commitada, volte ao nome de branch que anotou e inspecione o histórico com `git log --all --oneline --graph --decorate`.

Por fim, edite um arquivo rastreado, prepare a mudança, inspecione o diff e retire-a do staging com `git restore --staged -- arquivo`. Confirme com `git status` que a edição continua na working tree. Não use `git restore -- arquivo` nem `git reset --hard` nessa etapa.

