---
arquivo_id: "f1-3-2-01-integracao-e-mensagens-commit-04-pratica-guiada-integracao"
parent_key: "3.2"
tipo_arquivo: "practice"
assunto: "01_integracao_e_mensagens_commit"
ordem: 1
itens_origem: ["P1"]
---

## Prática — três níveis

Faça as atividades em repositórios locais descartáveis, com arquivos fictícios. Antes de integrar, confira `git status` e conclua ou preserve mudanças locais. Não reescreva histórico compartilhado.

### 1. Guiada — escolha a integração pelo objetivo

Considere este histórico, com `main` atualmente selecionada:

```text
A---B  main
 \
  C---D  feature
```

Escolha uma operação para cada objetivo e explique o efeito no histórico:

1. Integrar todo o trabalho da branch `feature`, mantendo a relação entre as linhas de desenvolvimento visível.
2. Reaplicar os commits `C` e `D` sobre `main` para deixar a linha de trabalho privada mais linear.
3. Trazer apenas a correção registrada em `D` para `main`, sem integrar o restante da branch.

