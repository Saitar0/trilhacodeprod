---
arquivo_id: "f6-25-2-90-integracao-p03-pratica-md"
parent_key: "25.2"
tipo_arquivo: "practice"
assuntos: ["01_estado_snapshot_formulario_controlado", "02_eventos_atualizadores", "03_colecoes_imutaveis_identidade"]
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Corrija uma lista com estado defeituoso

**Desafio:** diagnostique quatro defeitos: atualizar tarefa com mutação direta, key por índice, executar handler no JSX e campo com value sem onChange.

**Passos:**
1. Localize para cada defeito a regra React que está sendo violada.
2. Reescreva atualização de tarefa com map e cópia do item.
3. Substitua key por ID estável da tarefa.
4. Passe a referência do handler ou uma função que o invoque somente no evento.
5. Conecte value a onChange e teste digitação, envio e remoção/reordenação.

**Dica:** diferencie a função handler do resultado de chamá-la; um handler não deve rodar enquanto React calcula a interface.

