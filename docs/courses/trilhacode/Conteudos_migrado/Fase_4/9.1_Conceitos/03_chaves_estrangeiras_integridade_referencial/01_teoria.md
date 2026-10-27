---
arquivo_id: "f4-9-1-03-chaves-estrangeiras-integridade-referencial-01-teoria"
parent_key: "9.1"
tipo_arquivo: "theory"
assunto: "03_chaves_estrangeiras_integridade_referencial"
ordem: 3
itens_origem: ["3. Chave estrangeira e integridade referencial"]
---

### 3. Chave estrangeira e integridade referencial
Uma chave estrangeira (FK) contém valor que referencia uma chave primária ou outra chave única de uma tabela referenciada. Ela expressa a relação entre registros e permite ao SGBD rejeitar referências inexistentes. Uma FK não substitui a PK da própria linha: cada uma tem um papel diferente.

```sql
CREATE TABLE pessoa (
  id integer PRIMARY KEY,
  nome text NOT NULL
);

CREATE TABLE telefone (
  id integer PRIMARY KEY,
  pessoa_id integer NOT NULL REFERENCES pessoa(id),
  numero text NOT NULL
);
```

Aqui, pessoa_id liga cada telefone a uma pessoa; NOT NULL exige que toda linha de telefone tenha essa referência. Sem NOT NULL, uma FK pode aceitar NULL conforme as regras do SGBD. Uma FK pode referenciar uma PK ou colunas com restrição de unicidade. Detalhes de sintaxe e ações ao atualizar/remover linhas variam por SGBD.

**Erro comum:** acreditar que escrever um nome de coluna como pessoa_id cria uma relação automaticamente. A referência precisa ser declarada como FK no esquema.

