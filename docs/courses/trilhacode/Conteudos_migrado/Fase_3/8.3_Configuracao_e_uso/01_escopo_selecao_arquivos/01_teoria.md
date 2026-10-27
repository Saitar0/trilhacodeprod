---
arquivo_id: "f3-8-3-01-escopo-selecao-arquivos-01-teoria"
parent_key: "8.3"
tipo_arquivo: "theory"
assunto: "01_escopo_selecao_arquivos"
ordem: 1
itens_origem: ["1. Escopo do projeto e seleção de arquivos"]
---

## Teoria

### 1. Escopo do projeto e seleção de arquivos
A presença de tsconfig.json identifica a raiz de um projeto TypeScript e registra os arquivos de entrada e as opções do compilador. include, exclude e files ajudam a definir o escopo. rootDir e outDir organizam caminhos de entrada e saída; rootDir não seleciona quais arquivos serão compilados.

Ao executar tsc sem nomes de arquivo, o compilador usa a configuração encontrada para o projeto. Se você chamar tsc src/index.ts, os arquivos informados são compilados com opções padrão e os tsconfig.json são ignorados. Para usar uma configuração específica, execute tsc -p caminho/para/tsconfig.json ou rode tsc na raiz configurada.

**Erro comum:** achar que include está funcionando quando a linha de comando passou nomes de arquivos diretamente. Confira como o compilador foi iniciado e quais arquivos incluiu.

