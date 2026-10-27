---
arquivo_id: "f5-22-1-01-resumo"
parent_key: "22.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- O módulo raiz e os módulos de feature compõem o grafo de dependências da aplicação.
- Controllers adaptam HTTP; providers oferecem capacidades injetáveis e podem representar serviços, adaptadores ou fábricas.
- Providers são encapsulados; exports definem a API de um módulo e imports tornam essa API disponível.
- Interfaces TypeScript não existem no runtime; use classe ou token explícito para resolver providers.
- Evite registrar cópias, globalizar por conveniência ou esconder ciclos com forwardRef sem revisar a fronteira.
- Testes Nest podem substituir providers, mas devem corresponder à pergunta: unidade, configuração de módulo ou fluxo de integração.

