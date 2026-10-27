---
arquivo_id: "f4-14-1-01-documentos-colecoes-flexibilidade-01-teoria"
parent_key: "14.1"
tipo_arquivo: "theory"
assunto: "01_documentos_colecoes_flexibilidade"
ordem: 1
itens_origem: ["1. Entenda documentos, coleções e estrutura flexível"]
---

## Teoria

### 1. Entenda documentos, coleções e estrutura flexível
MongoDB armazena documentos BSON agrupados em coleções. BSON representa valores como texto, números, datas, arrays, objetos embutidos e ObjectId. Cada documento possui um campo `_id) único na coleção, gerado automaticamente quando não é informado.

Documentos da mesma coleção não precisam ter exatamente os mesmos campos ou tipos. Essa flexibilidade facilita representar variações do domínio, mas não elimina a necessidade de um modelo: aplicações ainda precisam saber quais campos são esperados, que tipos usam e como serão consultados. Validação de schema pode rejeitar documentos que não respeitam regras estabelecidas.

**Exemplo:** produtos de categorias diferentes podem ter atributos específicos, mas todos podem manter campos comuns como nome, categoria e ativo. Decida explicitamente se a variação é intencional ou um erro de escrita.

**Erro comum:** interpretar “schema flexível” como “qualquer formato de documento é seguro”.

