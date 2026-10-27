---
arquivo_id: "f3-8-1-90-integracao-kp02-gabarito-contratos-tarefas"
parent_key: "8.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_unions_narrowing", "03_inferencia_contratos_forma_objetos"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:**
```ts
type StatusTarefa = "aberta" | "em-andamento" | "concluida";

interface Tarefa {
  id: number;
  titulo: string;
  status: StatusTarefa;
  descricao?: string;
}

function formatarTarefa(tarefa: Tarefa): string {
  const descricao = tarefa.descricao ?? "Sem descrição";
  return tarefa.titulo + " — " + tarefa.status + ": " + descricao;
}

function mudarStatus(tarefa: Tarefa, novoStatus: StatusTarefa): Tarefa {
  return { ...tarefa, status: novoStatus };
}

const tarefa = { id: 1, titulo: "Estudar", status: "aberta" as StatusTarefa };
const atualizada = mudarStatus(tarefa, "em-andamento");
// mudarStatus(tarefa, "pausada"); // erro: literal fora da union
```

A asserção no exemplo só fixa o tipo do literal para ilustrar a chamada; uma alternativa mais clara é declarar `const tarefa: Tarefa`. A atualização retorna outro objeto e mantém a entrada intacta.

