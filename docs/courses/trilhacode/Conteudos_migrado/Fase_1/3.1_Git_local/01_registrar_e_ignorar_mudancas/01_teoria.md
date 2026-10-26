---
arquivo_id: "f1-3-1-01-registrar-e-ignorar-mudancas-01-teoria"
parent_key: "3.1"
tipo_arquivo: "theory"
assunto: "01_registrar_e_ignorar_mudancas"
ordem: 1
itens_origem: ["Repositório, working tree e staging area", "`.gitignore`"]
---

## Teoria

### Repositório, working tree e staging area
Git é um sistema distribuído de controle de versão. Um **repositório** contém o histórico de commits e metadados que permitem comparar e recuperar estados registrados. A **working tree** é o conjunto de arquivos que você está vendo e editando. A **staging area** (índice) reúne as mudanças escolhidas para o próximo commit.

O ciclo comum é: editar arquivos, verificar `git status`, examinar `git diff`, selecionar mudanças com `git add` e registrar com `git commit`. O commit guarda um snapshot do conteúdo selecionado no staging. Alterações que não foram adicionadas não entram automaticamente no commit.

```bash
git init
git status
git add README.md
git diff --staged
git commit -m "docs: add study repository overview"
```

### `.gitignore`
Um arquivo `.gitignore` indica padrões de arquivos ainda não rastreados que o Git deve ignorar, como artefatos gerados e arquivos locais. Ele não remove do histórico um arquivo que já está sendo rastreado. Não use `.gitignore` como substituto para remover segredos já commitados; credenciais expostas devem ser revogadas/rotacionadas e o histórico tratado com cuidado.

