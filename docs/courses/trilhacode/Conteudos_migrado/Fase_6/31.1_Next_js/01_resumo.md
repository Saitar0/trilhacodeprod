---
arquivo_id: "f6-31-1-01-resumo-md"
parent_key: "31.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- O App Router usa convenções de arquivo em `app`; `pages/api` pertence ao Pages Router e Route Handlers ficam em `app`.
- Server Components são padrão; Client Components são fronteiras de interação e seus imports entram na árvore cliente.
- Prerenderização, execução por requisição, streaming e trabalho no cliente podem coexistir; frescor e cache dependem da configuração e da versão.
- Route Handlers são endpoints públicos que precisam validar entrada, autenticar e autorizar operações.
- O destino de deploy deve suportar os runtimes e recursos usados, e variáveis expostas ao cliente não podem conter segredos.

