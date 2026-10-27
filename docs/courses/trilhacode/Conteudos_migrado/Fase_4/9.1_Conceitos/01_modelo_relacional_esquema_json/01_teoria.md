---
arquivo_id: "f4-9-1-01-modelo-relacional-esquema-json-01-teoria"
parent_key: "9.1"
tipo_arquivo: "theory"
assunto: "01_modelo_relacional_esquema_json"
ordem: 1
itens_origem: ["1. Tabelas, linhas, colunas e esquema", "5. Modelo relacional e representação JSON"]
---

## Teoria

### 1. Tabelas, linhas, colunas e esquema
Um banco de dados é uma coleção organizada de dados gerida por um sistema de gerenciamento (SGBD), que oferece formas controladas de armazenar, consultar e alterar informação. No modelo relacional, uma tabela agrupa ocorrências sobre um assunto; cada linha representa uma ocorrência e cada coluna um atributo com tipo definido. O esquema descreve tabelas, colunas, tipos e restrições; os dados são as ocorrências armazenadas.

O nome da tabela costuma representar a entidade ou relação, como pessoa ou pedido; nomes de coluna descrevem atributos, como nome ou criado_em. A ordem das linhas não é garantida sem ordenação explícita numa consulta. Também não presuma que duas linhas idênticas serão automaticamente impedidas: defina chaves e restrições que expressem as regras desejadas.

**Erro comum:** confundir posição de uma linha com identidade. A linha que aparece primeiro numa consulta não tem identidade estável por ocupar aquela posição.

### 5. Modelo relacional e representação JSON
O modelo relacional organiza entidades e relações em estruturas declaradas, com chaves e restrições. JSON é um formato de representação/intercâmbio de dados. Um banco relacional pode oferecer colunas que armazenam JSON, mas isso não transforma automaticamente o sistema num banco documental nem elimina as decisões sobre relações, identificadores e integridade.

Escolha a representação conforme consultas e regras que precisam ser sustentadas. Se pedidos precisam apontar para clientes e itens para produtos, uma referência explícita pode ser central para a integridade e para consultas. A modelagem detalhada e normalização serão aprofundadas nas próximas unidades; aqui, identifique o assunto de cada tabela e como as linhas se relacionam.

**Erro comum:** achar que “usa JSON” e “é banco relacional” são categorias mutuamente exclusivas. JSON pode ser um formato de dados dentro de uma coluna; modelo e garantias dependem do SGBD e do desenho adotado.

