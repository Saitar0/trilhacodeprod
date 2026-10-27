---
arquivo_id: "f5-24-3-01-escopo"
parent_key: "24.3"
tipo_arquivo: "project_scope"
ordem: 0
itens_origem: ["Contexto e escopo"]
---

## Contexto e escopo
Continue a ideia escolhida no projeto 3.5 e o modelo/banco produzido em 16.2. Esta entrega transforma o modelo e as funcionalidades anteriores em uma fatia vertical utilizável: cliente → API autenticada → regra de domínio → PostgreSQL, com cache apenas onde já exista um caso justificado da Fase 4. Não é necessário reescrever o projeto nem adotar arquitetura distribuída.

Use o framework e ORM já escolhidos no projeto. Se o curso ainda não fixou uma stack, a trilha de referência pode usar NestJS com Prisma; mantenha a alternativa adotada consistente e registre a decisão. As migrations são a fonte versionada do schema. Nunca use dados, credenciais ou banco de produção nos testes; forneça valores de exemplo sem segredos reais.

