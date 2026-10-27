---
arquivo_id: "f4-9-2-02-cardinalidade-opcionalidade-01-teoria"
parent_key: "9.2"
tipo_arquivo: "theory"
assunto: "02_cardinalidade_opcionalidade"
ordem: 2
itens_origem: ["3. Descreva cardinalidade e opcionalidade"]
---

### 3. Descreva cardinalidade e opcionalidade
Para cada lado da relação, indique mínimo e máximo. Em “um curso tem zero ou muitas matrículas”, Curso participa de 0..N matrículas; cada Matrícula pertence a exatamente 1 Curso. Em “um estudante pode ainda não ter se matriculado”, a participação do estudante é 0..N. O mínimo registra opcionalidade; o máximo diferencia uma ocorrência de várias.

Uma relação 1:N costuma ser representada pela FK no lado N. Uma relação 1:1 precisa de uma regra de unicidade na referência para impedir várias linhas apontando para a mesma ocorrência. Uma relação N:N precisa de uma tabela associativa, que pode ter atributos próprios da associação: quantidade em um item de pedido, data em uma matrícula ou papel de uma pessoa em um projeto.

Ao converter opcionalidade para colunas, considere a regra em cada direção. Uma FK anulável permite que a linha filha não tenha referência; uma FK não anulável exige uma referência. Restrições relacionais e outros mecanismos podem ser necessários para regras mais amplas, tema aprofundado na unidade 9.3.

**Erro comum:** desenhar uma linha entre duas entidades sem registrar quantidades nem participação mínima, deixando regras importantes ambíguas.

