---
arquivo_id: "f3-8-2-90-integracao-kp03-gabarito-catalogo"
parent_key: "8.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_formas_dados_unions", "02_generics_composicao_contratos", "03_unknown_validacao_runtime"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** se `ehProduto(valor)` for verdadeiro, retorne `{ estado: "sucesso", dados: valor }`; caso contrário, `{ estado: "erro", mensagem: "Dados do produto inválidos" }`. Um produto com preço string e `null` devem ser rejeitados. `primeiro<Produto>([])` resulta em `undefined`; o tipo de retorno é `Produto | undefined`.

**Entregáveis:** tipos nomeados, guarda, função que produz o resultado, três exemplos e explicação da diferença entre verificação estática e validação runtime.

