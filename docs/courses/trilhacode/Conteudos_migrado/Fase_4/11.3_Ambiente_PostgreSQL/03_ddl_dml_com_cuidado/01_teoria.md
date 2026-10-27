---
arquivo_id: "f4-11-3-03-ddl-dml-com-cuidado-01-teoria"
parent_key: "11.3"
tipo_arquivo: "theory"
assunto: "03_ddl_dml_com_cuidado"
ordem: 3
itens_origem: ["3. Crie tabelas e altere dados com cuidado"]
---

### 3. Crie tabelas e altere dados com cuidado
DDL define a estrutura; DML insere, consulta, altera e remove linhas. Um fluxo simples pode criar tabelas, inserir dados e verificar os resultados:

```sql
CREATE TABLE cliente (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome text NOT NULL
);

CREATE TABLE pedido (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  cliente_id integer NOT NULL REFERENCES cliente(id),
  status text NOT NULL,
  total numeric(10,2) NOT NULL CHECK (total >= 0)
);

INSERT INTO cliente (nome) VALUES ('Ana') RETURNING id, nome;
```

UPDATE e DELETE precisam de um alvo claro. Antes de alterar, execute como SELECT o mesmo filtro e confira as linhas. Acrescente WHERE de acordo com uma chave ou regra suficientemente específica. RETURNING mostra as linhas afetadas e é útil para confirmar o resultado no PostgreSQL.

```sql
UPDATE pedido
SET status = 'pago'
WHERE id = 42
RETURNING id, status;
```

Sem WHERE, UPDATE altera todas as linhas e DELETE remove todas as linhas da tabela. Um filtro com valor errado também pode atingir zero linhas, então confira a contagem e o resultado em vez de assumir que houve uma alteração.

**Erro comum:** executar UPDATE ou DELETE diretamente sem primeiro conferir o conjunto de linhas que o filtro seleciona.

