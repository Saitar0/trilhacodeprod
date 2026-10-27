---
arquivo_id: "f5-20-2-01-resumo"
parent_key: "20.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Senhas exigem hash adaptativo apropriado, salt único e parâmetros calibrados; nunca texto puro, criptografia reversível ou hash rápido simples.
- Valores SQL são parâmetros vinculados; identificadores variáveis vêm de allowlist ou de desenho que evite SQL dinâmico.
- CORS controla leitura cross-origin em navegadores; não substitui autenticação, autorização ou CSRF.
- Cookies enviados automaticamente exigem defesa CSRF para operações de estado; SameSite é geralmente uma camada adicional.
- Segredos não pertencem a código, histórico, imagens ou logs; uma credencial exposta precisa ser revogada/trocada.

