---
arquivo_id: "f3-8-3-01-resumo"
parent_key: "8.3"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- tsconfig.json define o escopo e as opções; rootDir não seleciona arquivos de entrada.
- tsc sem lista de arquivos usa a configuração; passar arquivos diretamente pode ignorá-la.
- target, module e moduleResolution devem corresponder ao runtime e ao build.
- noEmit transfere a emissão para outra ferramenta; mantenha saída fora das fontes.
- Checagem limpa cobre somente arquivos e regras configuradas, não prova funcionamento em runtime.
- allowJs e checkJs ajudam na migração gradual; converta um módulo por vez e valide o comportamento.

