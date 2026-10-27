---
arquivo_id: "f3-6-4-01-node-execucao-modulos-01-teoria"
parent_key: "6.4"
tipo_arquivo: "theory"
assunto: "01_node_execucao_modulos"
ordem: 1
itens_origem: ["Node.js e execução fora do navegador"]
---

## Teoria

### Node.js e execução fora do navegador
**Node.js** é um ambiente de execução de JavaScript fora do navegador. O comando `node arquivo.js` executa um arquivo. APIs do navegador, como `document` e `window`, não existem automaticamente no Node; use APIs próprias do runtime para arquivos, terminal e outros recursos do sistema. Um gerenciador de versões permite alternar entre versões quando projetos exigem versões distintas; consulte a documentação oficial no momento da instalação.

Node suporta módulos CommonJS (`require`, `module.exports`) e ECMAScript Modules (`import`, `export`). A interpretação depende da extensão e configuração do pacote, incluindo o campo `type` do `package.json`: `.mjs` e `.cjs` explicitam formatos; em arquivos `.js`, declare `"type": "module"` ou `"type": "commonjs"` no manifesto. Para este curso, escolha um formato por projeto e documente essa escolha.

