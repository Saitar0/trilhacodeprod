---
arquivo_id: "f4-9-1-02-chaves-primarias-identificacao-01-teoria"
parent_key: "9.1"
tipo_arquivo: "theory"
assunto: "02_chaves_primarias_identificacao"
ordem: 2
itens_origem: ["2. Chave primária e identificação"]
---

### 2. Chave primária e identificação
Uma chave primária (PK) identifica uma linha sem ambiguidade. O valor ou combinação de valores da PK é único e não nulo. A chave pode ser natural, quando um atributo do domínio já é identificador adequado, ou substituta, quando se cria um identificador técnico. Uma chave composta usa mais de uma coluna, por exemplo duas referências numa tabela associativa.

Uma chave natural só é uma boa candidata se sua estabilidade, unicidade e disponibilidade forem garantidas pelo domínio. Nomes de pessoas, por exemplo, normalmente não são bons identificadores. Uma PK substituta identifica a linha, enquanto outras regras — como email único, quando essa regra realmente pertence ao domínio — podem ser expressas separadamente com restrições apropriadas.

**Erro comum:** escolher um campo porque “parece único” sem verificar se pode mudar, faltar ou repetir.

