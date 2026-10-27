---
arquivo_id: "f6-25-2-90-integracao-p02-pratica-md"
parent_key: "25.2"
tipo_arquivo: "practice"
assuntos: ["01_estado_snapshot_formulario_controlado", "04_valores_derivados_condicoes_filtros"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Adicione filtros e estados de interface

**Desafio:** estenda a lista para mostrar todas, ativas ou concluídas; apresente contagem e mensagens diferentes para lista vazia e filtro sem resultados.

**Passos:**
1. Adicione um estado filter com valor inicial explícito.
2. Crie controles para alterar filtro; os handlers devem passar função ou valor correto.
3. Derive visibleTasks e completedCount de tasks e filter.
4. Diferencie “ainda não há tarefas” de “há tarefas, mas o filtro não encontra resultados”.
5. Verifique que concluir ou remover item atualiza contagem e lista filtrada.

**Dica:** a coleção completa responde se há alguma tarefa; a coleção filtrada responde se há resultado neste filtro.

