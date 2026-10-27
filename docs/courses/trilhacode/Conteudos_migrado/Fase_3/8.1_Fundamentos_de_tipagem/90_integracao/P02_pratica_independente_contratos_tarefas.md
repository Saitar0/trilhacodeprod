---
arquivo_id: "f3-8-1-90-integracao-p02-pratica-independente-contratos-tarefas"
parent_key: "8.1"
tipo_arquivo: "practice"
assuntos: ["02_unions_narrowing", "03_inferencia_contratos_forma_objetos"]
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — modele tarefas com contratos claros
Modele uma tarefa usando `interface Tarefa` e `type StatusTarefa` como union de literais. Inclua `id`, `titulo`, `status` e uma `descricao` opcional. Escreva:
- `formatarTarefa(tarefa)`, que retorna uma linha descritiva e trata descrição ausente;
- `mudarStatus(tarefa, novoStatus)`, que devolve uma nova tarefa com status atualizado;
- um exemplo válido e um exemplo inválido de status que o verificador deve rejeitar.

Use inferência nas variáveis locais quando o tipo já estiver claro. Anote entradas e saídas das funções, justificando as anotações escolhidas.

**Dica:** combine `??` com a propriedade opcional; para atualizar sem alterar o objeto recebido, use uma cópia com spread e o novo status.

