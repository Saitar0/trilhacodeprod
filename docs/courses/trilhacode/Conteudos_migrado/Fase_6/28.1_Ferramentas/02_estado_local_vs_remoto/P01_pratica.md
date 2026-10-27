---
arquivo_id: "f6-28-1-02-estado-local-vs-remoto-p01-pratica-md"
parent_key: "28.1"
tipo_arquivo: "practice"
assunto: "02_estado_local_vs_remoto"
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Faça um mapa de responsabilidades
**Objetivo:** classificar dados por origem, escopo e ciclo de vida antes de escolher uma biblioteca.

**Passos:**
1. Descreva uma aplicação pequena de catálogo com busca, filtros, lista de produtos, favoritos temporários e tema visual.
2. Para cada dado, preencha: onde nasce, quem o altera, quais telas o usam, se vem do servidor e quando deve desaparecer.
3. Atribua cada dado a estado local, URL, store de cliente ou cache de consulta remota; justifique cada escolha em uma frase.
4. Marque casos em que a escolha depende de um requisito ainda desconhecido, como sobreviver ao recarregamento ou permitir compartilhar um link.
5. Desenhe as fronteiras entre componentes, store, URL e API, incluindo quem pode atualizar cada dado.

**Dica:** não escolha a ferramenta pelo número de componentes. Primeiro identifique a origem e o ciclo de vida do dado.

**Entrega:** tabela de classificação e diagrama simples das fontes de estado.

**Critérios de conclusão:** cada dado tem fonte definida; estado local não foi globalizado sem justificativa; decisões dependentes de requisitos estão identificadas.

