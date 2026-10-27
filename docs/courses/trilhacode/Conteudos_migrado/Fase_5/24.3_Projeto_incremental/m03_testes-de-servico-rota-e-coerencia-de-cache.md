---
arquivo_id: "f5-24-3-m03-testes-de-servico-rota-e-coerencia-de-cache"
parent_key: "24.3"
tipo_arquivo: "milestone"
ordem: 3
itens_origem: ["M3"]
titulo_marco: "Marco 3 — Testes de serviço/rota e coerência de cache"
---

### Marco 3 — Testes de serviço/rota e coerência de cache
**Objetivo:** provar regras de negócio e integração crítica sem depender de dados externos.

**Tarefas:** crie testes unitários para regra de domínio e testes de rota ou integração que alcancem banco de teste isolado. Inclua sucesso, validação, não autenticado, acesso negado, recurso inexistente e persistência. Se houver cache no fluxo, demonstre hit, expiração/invalidação após escrita e fallback quando Redis estiver indisponível conforme a política definida. Se não houver cache adequado, registre por que não usar um é a decisão correta.

**Evidência:** suíte automatizada, configuração isolada, comandos, relatório de execução e nota explicando o que cada nível de teste cobre ou não cobre.

**Dica:** mock de repositório ajuda a isolar unidade, mas sozinho não demonstra que rota, ORM e PostgreSQL funcionam juntos. Nomeie claramente cada tipo de teste.

