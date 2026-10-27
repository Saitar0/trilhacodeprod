---
arquivo_id: "f6-31-1-02-fronteira-e-renderizacao-01-teoria-md"
parent_key: "31.1"
tipo_arquivo: "theory"
assunto: "02_fronteira_e_renderizacao"
ordem: 2
itens_origem: ["## Microtópico 2 — Desenhe fronteiras pequenas entre servidor e cliente", "## Microtópico 3 — Escolha quando e onde o conteúdo é produzido"]
---

## Microtópico 2 — Desenhe fronteiras pequenas entre servidor e cliente
No App Router, componentes de servidor são o padrão. Eles podem buscar dados próximos à fonte, usar credenciais de servidor e evitar enviar ao navegador JavaScript de interação que não é necessário. Um **Client Component** é necessário para estado interativo, event handlers e APIs do navegador. A diretiva `'use client'` marca uma entrada para a árvore cliente; os imports dessa entrada também participam do bundle cliente. Por isso, coloque a fronteira perto da interação em vez de marcar toda a aplicação como cliente.

Uma composição comum é um Server Component carregar dados e entregar apenas os valores necessários para um pequeno componente cliente, como um botão de favorito. Props que atravessam a fronteira precisam ser serializáveis conforme as regras do framework. A interface pode receber HTML inicial e o payload necessário para reconciliar a árvore; o JavaScript hidrata partes cliente para habilitar interações.

Código no servidor pode acessar segredos, mas valores passados ao cliente deixam de ser secretos. Em Next.js, variáveis com prefixo `NEXT_PUBLIC_` são incluídas no bundle cliente. Nunca envie tokens privados, credenciais de banco ou dados de autorização para um Client Component só para facilitar uma interação. A fronteira de componente também não substitui autenticação e autorização: proteja dados e ações no servidor.

## Microtópico 3 — Escolha quando e onde o conteúdo é produzido
Renderização descreve quando a interface ou parte dela é preparada; não trate SSR, prerenderização e client rendering como três caixas sempre excludentes. Uma página pode apresentar um shell previamente renderizado e carregar partes dinâmicas depois. A estratégia adequada depende de frescor, personalização, latência, custo de execução e capacidade do destino de deploy.

- **Prerenderização:** prepara HTML antes da solicitação do usuário quando os dados e a configuração permitem. Pode reduzir trabalho por visita e favorecer cache, mas precisa de uma política para atualizar conteúdo.
- **Renderização por solicitação:** usa dados ou contexto da requisição, como sessão e cookies, para compor conteúdo específico. Ajuda com personalização e frescor, mas depende de runtime e pode aumentar a latência.
- **Renderização no cliente:** o navegador executa JavaScript para produzir ou atualizar a interface. É útil para interações, mas pode exigir mais código e trabalho no cliente e não deve ser a escolha automática para todo conteúdo.

Streaming com limites de carregamento pode enviar partes da interface conforme ficam prontas. Cache e revalidação afetam se uma parte é calculada em build, em requisição ou reutilizada. As regras e padrões de cache do Next.js mudam entre versões e opções como Cache Components; confirme o comportamento da versão do projeto e teste o build de produção. Não deduza estratégia de renderização apenas pela aparência da página no servidor de desenvolvimento.

