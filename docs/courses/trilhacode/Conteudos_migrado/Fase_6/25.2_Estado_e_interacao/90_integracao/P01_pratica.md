---
arquivo_id: "f6-25-2-90-integracao-p01-pratica-md"
parent_key: "25.2"
tipo_arquivo: "practice"
assuntos: ["01_estado_snapshot_formulario_controlado", "03_colecoes_imutaveis_identidade"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Construa uma lista interativa

**Desafio:** implemente uma lista de tarefas que permita adicionar, concluir e remover itens sem mutar estado.

**Passos:**
1. Defina tarefa com id, title e completed e inicialize estado com lista vazia.
2. Crie um formulário com label e campo controlado para adicionar título.
3. No submit, impeça recarga, valide título não vazio após trim, crie ID estável uma vez e acrescente por meio de novo array.
4. Alterne conclusão usando map e remova usando filter.
5. Confirme que o estado de um cartão não troca de identidade quando outro item é removido.

**Dica:** gere ID ao tratar submit, não dentro de tasks.map durante a renderização.

