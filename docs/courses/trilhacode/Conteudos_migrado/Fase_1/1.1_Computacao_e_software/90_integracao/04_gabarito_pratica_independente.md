---
arquivo_id: "f1-1-1-90-integracao-04-gabarito-pratica-independente"
parent_key: "1.1"
tipo_arquivo: "answer_key_pratica"
ordem: 2
itens_origem: ["P2"]
---

**Referência para autocorreção**

```text
Fluxo público (um modelo possível):
pessoa → navegador (cliente)
navegador → DNS (se ainda precisar resolver o domínio)
navegador → servidor: requisição HTTP por /sobre
servidor → navegador: resposta HTTP com a página ou seus dados
navegador → pessoa: apresenta o conteúdo
Banco de dados: não é obrigatório; o conteúdo pode ser estático, estar em cache ou vir de outra fonte.

Fluxo da conta (um modelo possível):
pessoa → frontend: abre /minha-conta
navegador → servidor/API: requisição autenticada
backend → serviço de sessão e/ou banco: valida a sessão e busca dados necessários
backend → navegador: resposta HTTP com os dados permitidos ou um erro adequado
frontend → pessoa: apresenta o resultado
```

Há outras arquiteturas válidas. O essencial é manter as responsabilidades claras, mostrar requisição e resposta e não tratar DNS nem banco de dados como etapas invariáveis de qualquer navegação.

