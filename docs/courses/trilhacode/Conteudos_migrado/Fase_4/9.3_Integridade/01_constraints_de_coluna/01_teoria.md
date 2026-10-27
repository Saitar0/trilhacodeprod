---
arquivo_id: "f4-9-3-01-constraints-de-coluna-01-teoria"
parent_key: "9.3"
tipo_arquivo: "theory"
assunto: "01_constraints_de_coluna"
ordem: 1
itens_origem: ["1. Trate o banco como guardião das regras compartilhadas", "2. Identifique cada tipo de constraint"]
---

## Teoria

### 1. Trate o banco como guardião das regras compartilhadas
Integridade é a garantia de que os dados persistidos respeitam regras explícitas. Uma validação na interface melhora a experiência, mas pode ser contornada por outra tela, uma integração, um script ou uma requisição direta. A constraint no banco protege todas as formas de escrita que passam por ele.

Antes de escolher uma constraint, escreva a regra em linguagem de domínio e identifique o alcance: valor obrigatório, valor único, intervalo permitido, referência a outra linha ou regra entre linhas. Use a constraint mais próxima da regra. A aplicação continua útil para explicar o erro e orientar a pessoa, enquanto o banco mantém a garantia final comum.

**Exemplo:** “todo produto tem SKU, o SKU é único e o preço não pode ser negativo” resulta em regras distintas: NOT NULL, UNIQUE e CHECK.

**Erro comum:** repetir validações apenas no frontend e supor que os dados permanecerão válidos em qualquer caminho de escrita.

### 2. Identifique cada tipo de constraint
A chave primária (PRIMARY KEY) identifica cada linha, combina unicidade e ausência de NULL, e pode ser composta. Uma chave estrangeira (FOREIGN KEY) exige que a referência corresponda a uma chave elegível na tabela relacionada; se a coluna permitir NULL, uma referência ausente pode ser representada por NULL. NOT NULL exige um valor. UNIQUE impede duplicações conforme a semântica da constraint e do SGBD. CHECK verifica uma condição sobre a linha.

Exemplo em PostgreSQL:

```sql
CREATE TABLE produto (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  sku text NOT NULL UNIQUE,
  preco numeric(10,2) NOT NULL CHECK (preco >= 0)
);
```

No PostgreSQL, uma constraint CHECK considera válida uma expressão verdadeira ou desconhecida (NULL). Por isso, `CHECK (preco >= 0)` sozinho não exige preço: combine com NOT NULL quando a regra também exige presença. UNIQUE permite múltiplos NULL por padrão no PostgreSQL; se a regra considerar NULLs iguais, avalie `NULLS NOT DISTINCT` conforme a versão suportada.

**Erro comum:** acreditar que CHECK substitui NOT NULL ou que UNIQUE sempre impede mais de um NULL.

