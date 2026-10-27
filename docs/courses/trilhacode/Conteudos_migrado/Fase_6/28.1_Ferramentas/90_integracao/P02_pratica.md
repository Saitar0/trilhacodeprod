---
arquivo_id: "f6-28-1-90-integracao-p02-pratica-md"
parent_key: "28.1"
tipo_arquivo: "practice"
assuntos: ["01_criterio_de_escolha_vite_build", "02_estado_local_vs_remoto", "03_fronteiras_store_cache"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Integre uma lista remota e estado de interface
**Objetivo:** aplicar TanStack Query e Zustand em um fluxo pequeno com responsabilidades distintas.

**Passos:**
1. Em uma aplicação React com Vite, implemente ou localize uma tela de lista que consulte uma API ou mock.
2. Use TanStack Query para a consulta. Inclua na chave o filtro e a página usados pela função de busca.
3. Crie uma preferência de interface compartilhada, como painel de filtros aberto, em Zustand. Se essa preferência só for necessária em um componente, mantenha-a local e registre o motivo.
4. Faça uma alteração no servidor de teste e escolha uma política para atualizar a lista: invalidação ou atualização explícita do cache. Explique a escolha.
5. Registre a origem de cada dado e verifique que a resposta da consulta não foi duplicada em uma store sem sincronização.

**Dica:** uma variável só pertence à chave se mudar o conjunto de dados retornado; uma preferência puramente visual não precisa ser enviada à API.

**Entrega:** tela funcional, diagrama de responsabilidades e justificativa da política de atualização.

**Critérios de conclusão:** consulta e filtro permanecem coerentes; estado visual tem escopo justificado; a atualização não depende de duas cópias divergentes da resposta remota.

