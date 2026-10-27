---
arquivo_id: "f6-31-1-01-estrutura-rotas-app-router-p01-pratica-md"
parent_key: "31.1"
tipo_arquivo: "practice"
assunto: "01_estrutura_rotas_app_router"
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Modele rotas, páginas e layouts
**Objetivo:** transformar uma estrutura de produto em rotas do App Router sem confundir URL, organização de pastas e convenções.

**Passos:**
1. Modele um catálogo com início, listagem, detalhe por slug e uma área de conta.
2. Desenhe a árvore `app` e marque quais segmentos viram URL, quais grupos apenas organizam arquivos e onde layouts compartilhados são necessários.
3. Defina onde entrariam estados de carregamento, erro e não encontrado usando as convenções do framework.
4. Identifique quais URLs são páginas e quais recursos são endpoints HTTP; garanta que `page.tsx` e `route.ts` não disputem o mesmo segmento.
5. Registre quais rotas podem ser pré-geradas e quais dependem de dados da solicitação ou sessão, justificando a escolha.

**Dica:** escreva primeiro as URLs desejadas e depois mapeie cada uma para arquivos. A estrutura de pastas é uma convenção para expressar rotas, não o requisito em si.

**Entrega:** árvore de arquivos anotada e tabela URL → página/handler → dados necessários.

**Critérios de conclusão:** URLs e arquivos correspondem; layouts têm escopo claro; páginas públicas e dependentes de sessão estão diferenciadas.

