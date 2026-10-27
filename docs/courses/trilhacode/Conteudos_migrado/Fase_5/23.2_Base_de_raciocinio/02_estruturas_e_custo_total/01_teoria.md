---
arquivo_id: "f5-23-2-02-estruturas-e-custo-total-01-teoria"
parent_key: "23.2"
tipo_arquivo: "theory"
assunto: "02_estruturas_e_custo_total"
ordem: 2
itens_origem: ["Microtópico 3 — Compare operações e custo total"]
---

## Microtópico 3 — Compare operações e custo total

Considere uma lista com n registros e q buscas de ID. Cada busca linear pode inspecionar até n itens; q buscas podem exigir trabalho proporcional a q × n. Construir um índice em Map a partir da lista custa trabalho proporcional a n em condições usuais e usa memória adicional proporcional a n; depois, q consultas por chave tendem a ser sublineares conforme o contrato da plataforma. A comparação completa é, portanto, custo de construção + consultas + memória, não apenas “lista contra Map”.

Em JavaScript, a especificação exige que Map e Set ofereçam, em média, acesso sublinear no número de elementos; não exige necessariamente uma tabela hash nem promete O(1) para toda operação. Para discussão introdutória, é comum comparar busca linear O(n) com consulta esperada aproximadamente O(1) em uma tabela hash, deixando a hipótese explícita.

| Operação/necessidade | Estrutura candidata | Atenção |
|---|---|---|
| Acesso pela posição conhecida | Array/lista | Inserção ou remoção no meio pode exigir deslocar itens. |
| Busca por uma chave, muitas repetições | Map | Construir e manter o índice tem custo e consome memória. |
| Pertencimento sem valor associado | Set | A igualdade e a identidade dos valores influenciam o resultado. |
| Manter sequência de chegada | Array/fila | A implementação concreta da fila importa para remoções frequentes do início. |
| Consulta de registros persistidos | Consulta e índice no banco | Evite transferir todo o conjunto ao processo sem necessidade. |

Não confunda “um laço” com “O(n)” em todos os cenários nem “dois laços” automaticamente com O(n²): o limite depende dos intervalos, do trabalho dentro do laço e da relação entre as variáveis. Se um algoritmo ordena e depois percorre, o crescimento combinado pode ser O(n log n) + O(n), que é O(n log n) para n grande.

