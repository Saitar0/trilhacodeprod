---
arquivo_id: "f5-17-2-03-logs-contexto-seguro-p03-pratica"
parent_key: "17.2"
tipo_arquivo: "practice"
assunto: "03_logs_contexto_seguro"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Criar um registro de erro seguro
Defina um formato de log para uma falha em uma rota. Inclua um evento legível, timestamp, request ID, método/rota sem parâmetros pessoais, status, duração e classe ou código do erro. Prepare um exemplo de erro de autenticação e outro de banco. Liste campos que devem ser redigidos ou removidos. Use a saída de console apenas para demonstrar localmente e descreva como o projeto entregaria logs em execução normal.

**Dica:** não use o token do usuário como request ID. Um identificador aleatório de correlação serve para conectar eventos sem conceder acesso à conta.

