---
arquivo_id: "f10-53-4-t02"
parent_key: "53.4"
tipo_arquivo: "theory"
assunto: "02_estruturas_e_padroes"
ordem: 2
itens_origem: ["### 2. Escolher estrutura ou padrão pela operação"]
---


### 2. Escolher estrutura ou padrão pela operação
Use mapa hash para associar chaves a valores, contar frequências ou lembrar posições; conjunto para testar presença sem guardar valores associados; pilha para processar o item mais recente primeiro; fila para ordem de chegada. Essas operações têm custo médio esperado eficiente em implementações hash usuais, mas não constituem garantia universal para qualquer linguagem ou entrada.

Dois ponteiros podem evitar percorrer combinações quando a ordem ou a estrutura do problema permite mover limites com segurança. Janela deslizante é útil para intervalos contíguos quando a condição pode ser mantida ao incluir/remover elementos. Busca binária reduz o espaço de busca quando os dados estão ordenados ou quando existe uma condição monotônica. Em árvores e grafos, DFS/BFS visitam nós; marque visitados quando necessário para evitar ciclos e trabalho repetido.

Antes de aplicar um padrão, explique por que ele preserva a correção. Ordenar tudo pode simplificar uma solução, mas costuma adicionar custo O(n log n) e alterar a ordem original; use somente se isso ajuda os requisitos.

