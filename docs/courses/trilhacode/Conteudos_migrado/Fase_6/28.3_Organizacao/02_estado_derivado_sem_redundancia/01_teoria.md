---
arquivo_id: "f6-28-3-02-estado-derivado-sem-redundancia-01-teoria-md"
parent_key: "28.3"
tipo_arquivo: "theory"
assunto: "02_estado_derivado_sem_redundancia"
ordem: 2
itens_origem: ["## Microtópico 3 — Remova redundância e valores que podem ser derivados"]
---

## Microtópico 3 — Remova redundância e valores que podem ser derivados
Manter duas versões editáveis do mesmo fato exige sincronização e abre espaço para divergência. Se o carrinho armazena itens, por exemplo, o subtotal normalmente pode ser calculado a partir deles durante a renderização. Guardar também um subtotal independente cria o risco de atualizar os itens e esquecer o total.

Também evite combinações que permitem estados contraditórios. Se a interface tem uma aba ativa, guarde o identificador da aba em vez de vários booleanos que podem ficar verdadeiros ao mesmo tempo. Para seleção de um registro em uma lista, guarde seu identificador; derive o objeto selecionado da coleção atual. Isso evita uma referência antiga quando a lista é atualizada.

Nem toda cópia é erro. Um rascunho de formulário pode divergir intencionalmente do registro salvo porque representa uma edição ainda não confirmada. A distinção precisa estar explícita: qual dado é o original, qual é o rascunho e quando ocorre a confirmação ou o descarte. Estado derivado deve ser calculado; estado de edição tem um ciclo de vida próprio.

