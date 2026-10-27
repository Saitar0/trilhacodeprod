---
arquivo_id: "f4-11-2-01-resumo"
parent_key: "11.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- INNER JOIN retorna pares correspondentes; LEFT JOIN preserva as linhas da esquerda.
- A condição ON deve seguir a relação do modelo e a granularidade resultante precisa ser prevista.
- Junções 1:N podem repetir atributos do lado 1 e inflar agregações.
- WHERE filtra linhas; HAVING filtra grupos depois da agregação.
- EXISTS expressa presença sem multiplicar a linha externa; escolha pela semântica e verifique o plano se desempenho importar.

