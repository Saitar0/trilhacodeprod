---
arquivo_id: "f5-22-2-01-resumo"
parent_key: "22.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Tipos estáticos não validam JSON em runtime; escolha classe com decorators ou schema em runtime.
- Pipes validam/transformam argumentos; whitelist e rejeição de campos extras precisam de configuração adequada ao mecanismo.
- Guards usam contexto e metadados de rota, e executam antes dos pipes.
- Autenticação, política geral de rota, autorização do objeto, validação estrutural e regras de negócio são responsabilidades distintas.
- A resposta precisa de contrato próprio e allowlist de propriedades.

