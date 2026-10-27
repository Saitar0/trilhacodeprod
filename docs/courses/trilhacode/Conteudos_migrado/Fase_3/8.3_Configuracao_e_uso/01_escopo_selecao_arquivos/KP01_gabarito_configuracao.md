---
arquivo_id: "f3-8-3-01-escopo-selecao-arquivos-kp01-gabarito-configuracao"
parent_key: "8.3"
tipo_arquivo: "answer_key_pratica"
assunto: "01_escopo_selecao_arquivos"
ordem: 1
itens_origem: ["P1"]
---

**Solução esperada:** passar src/index.ts diretamente faz o compilador ignorar tsconfig.json e usar opções padrão para os arquivos indicados. Execute tsc -p . na raiz (ou tsc sem lista de arquivos nessa raiz). include seleciona arquivos; outDir define onde colocar a saída emitida.

