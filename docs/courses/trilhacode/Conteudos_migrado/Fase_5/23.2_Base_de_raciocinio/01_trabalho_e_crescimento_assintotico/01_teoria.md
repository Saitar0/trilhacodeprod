---
arquivo_id: "f5-23-2-01-trabalho-e-crescimento-assintotico-01-teoria"
parent_key: "23.2"
tipo_arquivo: "theory"
assunto: "01_trabalho_e_crescimento_assintotico"
ordem: 1
itens_origem: ["theory-container", "Microtópico 1 — Comece pelo trabalho que o programa faz", "Microtópico 2 — O que Big O explica e o que não explica"]
---

## Teoria

## Microtópico 1 — Comece pelo trabalho que o programa faz

Escolher uma estrutura começa com perguntas sobre o uso, não com o nome de uma estrutura “rápida”. Liste as operações necessárias e a frequência relativa delas: localizar por índice ou chave, verificar existência, preservar ordem, permitir duplicatas, inserir, remover ou percorrer todos os elementos. Registre também o tamanho típico e máximo do conjunto e se ele cabe em memória.

Uma lista é útil para manter uma sequência e percorrê-la. Um Map associa chaves a valores. Um Set representa uma coleção sem duplicatas segundo as regras de igualdade da linguagem. Uma fila modela processamento na ordem de chegada; uma pilha modela o último que entrou como o primeiro a sair. As estruturas oferecem compromissos diferentes: ordenar, encontrar, atualizar e percorrer não têm o mesmo custo.

Exemplo: uma tela recebe vinte produtos e precisa mostrá-los em ordem. Uma lista pode ser a escolha mais direta. Um processo que verifica repetidamente se milhares de IDs pertencem a um conjunto pode se beneficiar de um Set ou Map. Se os dados já estão no banco, porém, baixá-los todos para fazer a busca em memória pode ser a decisão errada; use a fronteira de consulta adequada.

## Microtópico 2 — O que Big O explica e o que não explica

Big O descreve um limite de crescimento do custo de um algoritmo à medida que o tamanho da entrada aumenta. Para comparar implementações, definimos o que conta como entrada (por exemplo, n itens) e qual recurso estamos analisando (operações, memória ou chamadas externas). A notação omite constantes e detalhes de máquina; ela não prevê diretamente milissegundos.

- **O(1):** custo limitado por uma constante em relação a n, no modelo analisado.
- **O(log n):** o problema é reduzido em uma proporção em cada etapa, como na busca binária em uma sequência ordenada.
- **O(n):** o trabalho cresce proporcionalmente ao número de itens, como percorrer uma lista para procurar um ID.
- **O(n log n):** crescimento comum de algoritmos eficientes de ordenação por comparação.
- **O(n²):** comparar cada item com todos os demais em dois laços pode produzir crescimento quadrático.

Big O não diz se uma operação O(1) é mais rápida, na prática, do que uma operação O(n) para todo n. Constantes, tamanho real, custo de alocação, localidade de memória, implementação e operação dominante importam. Também não descreve o custo de uma consulta remota se o modelo de análise conta apenas operações locais.

Diferencie os casos quando a escolha depende de hipótese: pior caso, caso médio/esperado e custo amortizado não são sinônimos. Uma tabela hash pode ter busca esperada muito eficiente sob hipóteses sobre distribuição e implementação; isso não garante que toda busca em qualquer implementação seja O(1). Uma lista dinâmica pode ocasionalmente copiar seus elementos ao crescer, embora inserir no fim seja amortizado O(1) ao longo de uma sequência de inserções.

