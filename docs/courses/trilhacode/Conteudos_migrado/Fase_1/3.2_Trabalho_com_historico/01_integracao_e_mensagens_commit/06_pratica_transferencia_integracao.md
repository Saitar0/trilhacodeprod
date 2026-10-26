---
arquivo_id: "f1-3-2-01-integracao-e-mensagens-commit-06-pratica-transferencia-integracao"
parent_key: "3.2"
tipo_arquivo: "practice"
assunto: "01_integracao_e_mensagens_commit"
ordem: 3
itens_origem: ["P3"]
---

### 3. Transferência — compare merge, rebase e cherry-pick

Em três repositórios descartáveis, crie um commit-base com `agenda.md` e anote o nome da branch inicial. Em cada repositório, faça mudanças pequenas em arquivos diferentes para evitar conflitos acidentais.

1. **Merge:** crie uma branch `feature/completa`, faça nela dois commits; volte à branch inicial, faça um commit independente e integre `feature/completa` com `git merge`. Inspecione `git log --all --oneline --graph --decorate`.
2. **Rebase:** parta de outro commit-base; crie `feature/privada` e faça dois commits; volte à branch inicial e faça um commit independente; retorne à branch privada e reaplique-a sobre a branch inicial com `git rebase <branch-inicial>`. Compare o grafo antes e depois e identifique que os commits reaplicados têm novos identificadores.
3. **Cherry-pick:** parta do terceiro commit-base; crie `feature/correcao`, faça um commit pequeno e anote seu identificador; volte à branch inicial e aplique somente esse commit com `git cherry-pick <identificador>`. Confirme que o commit original permanece na branch de origem e que a branch atual recebeu um novo commit.

Use mensagens que expliquem a intenção, como `docs: incluir frequência de publicação`. Registre para cada caso: objetivo, branch em que estava, comando de integração, efeito no grafo e risco relevante. Não publique essas branches nem reescreva histórico compartilhado.

