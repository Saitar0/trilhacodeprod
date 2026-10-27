---
arquivo_id: "f9-41-2-90-integracao-p02-pratica"
parent_key: "41.2"
tipo_arquivo: "practice"
assuntos: ["02_custo_prontidao_operacional", "03_descoberta_teste_fronteira"]
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Mapa de dependências e prontidão
**Contexto:** desenhe pedidos, estoque e notificações. Pedidos e estoque atualizam tabelas compartilhadas na mesma transação; notificações lê pedidos diretamente e não tem requisito de resposta imediata. Uma equipe de três pessoas mantém a aplicação.

**Instruções:** crie um mapa de módulos, chamadas, dados e equipes. Marque dependências que impediriam deploy independente. Proponha duas melhorias possíveis dentro do monólito e identifique o mínimo de contratos, ownership, observabilidade e operação que faltaria para extrair uma capacidade depois.

**Entrega:** diagrama simples e checklist de prontidão com campos “atendido”, “pendente” e evidência.

**Dica gradual:** trace quem lê e grava cada dado; depois observe quais operações dependem da mesma transação. Uma API interna não é limite real se todos ainda alteram diretamente os dados alheios.

