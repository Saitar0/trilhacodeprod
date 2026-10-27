---
arquivo_id: "f6-28-1-03-fronteiras-store-cache-01-teoria-md"
parent_key: "28.1"
tipo_arquivo: "theory"
assunto: "03_fronteiras_store_cache"
ordem: 3
itens_origem: ["## Microtópico 4 — Combine com fronteiras claras"]
---

## Microtópico 4 — Combine com fronteiras claras
As ferramentas podem coexistir, desde que cada uma tenha uma responsabilidade clara: Vite prepara desenvolvimento e build; Zustand mantém estado de cliente que realmente precisa ser compartilhado; TanStack Query coordena dados remotos. A consulta pode usar um filtro selecionado na interface, mas a aplicação deve decidir se esse filtro vive na URL, na store ou localmente. Se o filtro altera os resultados, a chave da consulta precisa refletir seu valor atual.

Quando uma mutação altera dados do servidor, escolha como as consultas relacionadas serão atualizadas: invalidar e buscar novamente, atualizar o cache de forma explícita ou combinar estratégias. Faça isso de acordo com o contrato da API e com o comportamento desejado. Evite sincronização improvisada em que um componente altera uma cópia na store e outro continua lendo uma resposta antiga do cache.

Não transporte uma receita de arquitetura sem considerar o projeto. Um framework pode integrar build, rotas ou carregamento de dados com outras ferramentas. Em outro caso, `fetch` e estado local podem atender ao escopo. Aprenda a reconhecer a responsabilidade; a escolha da implementação vem depois do contexto.

