---
arquivo_id: "f10-53-4-t03"
parent_key: "53.4"
tipo_arquivo: "theory"
assunto: "03_complexidade_e_correcao"
ordem: 3
itens_origem: ["### 3. Analisar tempo, espaço e correção"]
---


### 3. Analisar tempo, espaço e correção
Descreva a complexidade em função do tamanho da entrada. Uma varredura completa tende a O(n); dois percursos completos aninhados tendem a O(n²); busca binária em sequência ordenada tende a O(log n). Analise o trabalho real: laços sobre partes disjuntas não necessariamente somam n²; chamadas a funções e operações das estruturas também contam.

Espaço auxiliar é a memória adicional além da entrada, como um mapa com até n itens (O(n)) ou alguns índices/contadores (O(1)). Declare quando a entrada é modificada. Para defender correção, explique a propriedade mantida pelo algoritmo — por exemplo, quais elementos já foram considerados e por que nenhum candidato válido foi descartado.

