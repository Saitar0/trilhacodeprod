---
arquivo_id: "f3-8-2-02-generics-composicao-contratos-p02-pratica-independente-repositorio"
parent_key: "8.2"
tipo_arquivo: "practice"
assunto: "02_generics_composicao_contratos"
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — componha uma coleção genérica
Implemente `Repositorio<T>` com `listar(): T[]`, `buscarPorId(id: number): T | undefined` e `adicionar(item: T): void`. Restrinja `T` para exigir `id: number`. Use a implementação com dois modelos, como Produto e Usuario, sem recorrer a `any`.

**Dica:** uma interface `ComId { id: number }` pode ser usada como restrição. Preserve `T` nos itens armazenados e retornados.

