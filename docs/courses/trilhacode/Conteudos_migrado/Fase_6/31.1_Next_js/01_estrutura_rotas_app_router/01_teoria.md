---
arquivo_id: "f6-31-1-01-estrutura-rotas-app-router-01-teoria-md"
parent_key: "31.1"
tipo_arquivo: "theory"
assunto: "01_estrutura_rotas_app_router"
ordem: 1
itens_origem: ["## Microtópico 1 — Leia a estrutura de rotas do App Router"]
---

## Microtópico 1 — Leia a estrutura de rotas do App Router
Next.js é um framework React que reúne convenções de roteamento, renderização e build. No **App Router**, pastas dentro de `app` representam segmentos de URL; arquivos convencionais definem o que cada segmento faz. `page.tsx` expõe uma página, `layout.tsx` compartilha uma estrutura entre páginas filhas e `route.ts` publica um handler HTTP. Segmentos dinâmicos como `[slug]` representam partes variáveis do caminho. Um grupo de rotas entre parênteses pode organizar arquivos sem adicionar um segmento à URL.

Layouts aninhados preservam a estrutura compartilhada durante a navegação. Também existem convenções para estados de carregamento, erros e páginas não encontradas, como `loading.tsx`, `error.tsx` e `not-found.tsx`. Entenda o papel de cada arquivo antes de inventar um mecanismo próprio para o mesmo comportamento.

O **Pages Router** é uma convenção anterior baseada em `pages`; nele, arquivos em `pages/api` implementam API Routes. O App Router usa Route Handlers em `app`. Os dois roteadores podem coexistir em um projeto durante uma migração, mas não defina uma página e um Route Handler para o mesmo segmento de rota. Ao estudar ou manter um projeto, identifique qual roteador contém cada URL.

