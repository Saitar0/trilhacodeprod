---
arquivo_id: "f4-16-1-01-modelos-chave-valor-documentos-01-teoria"
parent_key: "16.1"
tipo_arquivo: "theory"
assunto: "01_modelos_chave_valor_documentos"
ordem: 1
itens_origem: ["1. Modelo de dados e acesso"]
---

## Teoria

### 1. Modelo de dados e acesso
DynamoDB é um banco gerenciado chave-valor e de documentos. A chave de partição determina como os itens são distribuídos e recuperados; uma chave de ordenação opcional organiza itens relacionados e permite consultas por faixa. O desenho começa pelos padrões de acesso previstos: quais itens precisam ser encontrados, por quais chaves e com que ordenação. Índices secundários podem dar suporte a outras consultas, com implicações de capacidade e manutenção. [AWS — modelagem de tabelas](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/data-modeling.html).

Cloud Firestore é um banco orientado a documentos: documentos com campos ficam em coleções, e podem conter objetos aninhados ou subcoleções. A forma dos documentos deve apoiar as leituras e escritas da aplicação. Consultas dependem de índices; combinações de campos podem exigir índices compostos. SDKs e recursos do ecossistema Firebase/Google Cloud podem ser parte importante da escolha. [Firebase — modelo de dados](https://firebase.google.com/docs/firestore/data-model) e [índices](https://firebase.google.com/docs/firestore/query-data/index-overview).

