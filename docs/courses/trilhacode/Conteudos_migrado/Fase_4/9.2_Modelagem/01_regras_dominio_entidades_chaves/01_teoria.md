---
arquivo_id: "f4-9-2-01-regras-dominio-entidades-chaves-01-teoria"
parent_key: "9.2"
tipo_arquivo: "theory"
assunto: "01_regras_dominio_entidades_chaves"
ordem: 1
itens_origem: ["1. Comece pelas regras e perguntas do domínio", "2. Identifique identidade, atributos e chaves"]
---

## Teoria

### 1. Comece pelas regras e perguntas do domínio
Antes de desenhar tabelas, registre quem usa o sistema, quais fatos precisam ser guardados e quais perguntas ele deve responder. Requisitos como “uma pessoa pode se matricular em vários cursos” e “cada matrícula pertence a uma pessoa e a um curso” revelam conceitos e relações. Telas ajudam a descobrir informações, mas não devem definir o modelo sozinhas: uma tela pode mudar sem que as regras do domínio mudem.

Uma entidade representa uma classe de coisas identificáveis, como Pessoa, Curso ou Matrícula. Um atributo descreve uma propriedade de uma entidade ou de uma relação, como nome da pessoa ou data da matrícula. Relações representam associações com significado no domínio. Para cada atributo, pergunte a que conceito ele pertence e se precisa ser armazenado. Evite guardar o mesmo fato em vários lugares sem uma razão clara.

**Exemplo:** se o sistema precisa listar cursos de cada estudante e a data em que cada inscrição aconteceu, “Estudante” e “Curso” são entidades; a inscrição é uma relação com atributo próprio. Tratar a data como propriedade do estudante seria incorreto, pois ela varia conforme o curso.

**Erro comum:** transformar cada tela ou seção visual em tabela sem verificar se representa um conceito do domínio.

### 2. Identifique identidade, atributos e chaves
Uma chave candidata identifica uma linha sem ambiguidade e não pode ser nula. A chave primária é a candidata escolhida como identificador principal. Uma chave natural vem do domínio, como um código oficial, e só é boa escolha se for única, estável e adequada como identificador. Não presuma que e-mail, nome ou telefone seja único ou imutável. Uma chave substituta, como um número gerado, reduz a dependência de regras externas, mas não substitui restrições de unicidade que o domínio exige.

Chaves estrangeiras representam referências entre tabelas. Uma chave composta combina mais de uma coluna; por exemplo, em uma matrícula pode ser necessário impedir que a mesma pessoa se inscreva duas vezes no mesmo curso. A escolha da chave deve refletir as regras: se a matrícula tiver identidade própria, ela pode usar um identificador substituto e ainda impor unicidade em (estudante_id, curso_id).

Documente também tipo, nulabilidade, unicidade e valor padrão quando fizerem parte das regras. Uma FK obrigatória no lado dependente expressa que cada linha filha aponta para um pai; ela não garante que todo pai já tenha uma linha filha.

**Erro comum:** criar um campo id e concluir que o modelo está íntegro, esquecendo de preservar regras como “código do curso não se repete”.

