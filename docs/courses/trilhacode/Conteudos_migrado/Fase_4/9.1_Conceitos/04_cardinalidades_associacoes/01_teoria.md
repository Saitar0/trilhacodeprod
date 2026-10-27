---
arquivo_id: "f4-9-1-04-cardinalidades-associacoes-01-teoria"
parent_key: "9.1"
tipo_arquivo: "theory"
assunto: "04_cardinalidades_associacoes"
ordem: 4
itens_origem: ["4. Cardinalidades: 1:1, 1:N e N:N"]
---

### 4. Cardinalidades: 1:1, 1:N e N:N
A cardinalidade descreve quantas ocorrências podem se relacionar:
- **1:1:** cada ocorrência de A se relaciona com no máximo uma de B, e vice-versa. Uma FK com unicidade ajuda a impor o limite de um lado; a obrigatoriedade depende também de NOT NULL e da regra de domínio.
- **1:N:** uma ocorrência do lado 1 pode se relacionar com várias do lado N. A FK normalmente fica na tabela do lado N, como pessoa_id em telefone.
- **N:N:** várias ocorrências de A podem se relacionar com várias de B. Represente o vínculo numa tabela associativa com FKs para ambas. A combinação das FKs pode ser uma PK composta quando o mesmo par só deve ocorrer uma vez.

Uma relação associativa também pode ter atributos próprios. Em matrícula, por exemplo, a data de inscrição pertence ao vínculo entre estudante e turma, não apenas ao estudante nem apenas à turma.

**Erro comum:** colocar uma lista de identificadores ou valores repetidos dentro de uma coluna para representar N:N. Isso dificulta validar referências, atualizar relações e consultar os dados de forma consistente.

