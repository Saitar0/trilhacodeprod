---
arquivo_id: "f1-3-3-02-pull-request-code-review-04-pratica-guiada-review"
parent_key: "3.3"
tipo_arquivo: "practice"
assunto: "02_pull_request_code_review"
ordem: 1
itens_origem: ["P1"]
---

## Prática — três níveis

Use repositórios próprios de estudo ou material fictício. Não envie credenciais reais, dados pessoais ou arquivos locais sensíveis ao remoto.

### 1. Guiada — faça uma revisão baseada no diff

Uma pull request chamada “Ajusta cálculo” altera esta função. O requisito diz que o total deve somar o imposto ao preço:

```diff
 function calcularTotal(preco, taxa) {
-  return preco + preco * taxa;
+  return preco - preco * taxa;
 }
```

Para `preco = 100` e `taxa = 0.10`, o resultado esperado é `110`.

**Tarefa:** escolha entre comentar, aprovar ou solicitar mudanças. Escreva um comentário curto que cite o comportamento observado, o caso que demonstra o problema e uma ação concreta para corrigir ou verificar. Mantenha o comentário respeitoso e ligado à mudança proposta.

