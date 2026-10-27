---
arquivo_id: "f4-10-2-01-resumo"
parent_key: "10.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Compose declara serviços e recursos para recriar um ambiente local.
- A rede padrão permite descobrir serviços pelo nome; portas internas servem à comunicação entre containers.
- Volumes nomeados persistem com `down`; `down --volumes` pode apagá-los.
- `depends_on` ordena a inicialização; healthcheck pode representar prontidão, e a aplicação ainda deve tolerar reconexões.
- Use portas e credenciais de acordo com o contexto e mantenha segredos reais fora do repositório.

