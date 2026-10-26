---
arquivo_id: "f1-3-3-90-integracao-03-pratica-independente-incidentes"
parent_key: "3.3"
tipo_arquivo: "practice"
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — responda a dois incidentes de colaboração

Escreva um procedimento curto para cada situação, em ordem, separando observação, decisão e ação:

1. O push foi rejeitado porque `origin` contém commits novos. Você não sabe se outras pessoas também usam a branch.
2. Um token real apareceu em um commit enviado ao remoto, mas a pull request ainda não foi integrada.

Inclua para cada caso: o que verificar primeiro, qual ação imediata reduz risco, o que não se deve presumir e quando envolver responsáveis pelo repositório. Não inclua comandos com segredos nem valores de tokens.

**Dicas progressivas**

- No caso do push, `git fetch` atualiza as referências remotas sem integrar por si só. Compare os históricos e siga a convenção acordada para merge ou rebase; não presuma que a branch é privada.
- No caso do segredo, removê-lo em um commit posterior não invalida o valor já exposto. A credencial precisa ser revogada/rotacionada; depois, trate o histórico e as cópias com os responsáveis.

