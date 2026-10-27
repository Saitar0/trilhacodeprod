---
arquivo_id: "f5-20-3-04-finalidade-retencao-e-logs-01-teoria"
parent_key: "20.3"
tipo_arquivo: "theory"
assunto: "04_finalidade_retencao_e_logs"
ordem: 4
itens_origem: ["Microtópico 4 — Registre finalidade e retenção com cautela"]
---

## Microtópico 4 — Registre finalidade e retenção com cautela
Para dados pessoais, registre o que é coletado, para qual finalidade do produto, quem acessa, onde é compartilhado e por quanto tempo é necessário. Revise se o sistema pode funcionar com menos dados e descarte ou anonimize conforme a política aplicável e as obrigações do controlador. Reduza dados em logs e ambientes de teste; use registros sintéticos quando possível.

A LGPD inclui princípios como finalidade, adequação, necessidade, segurança, prevenção e prestação de contas; consentimento não é a única base legal. Uma equipe de engenharia pode documentar os dados e implementar controles, mas não deve presumir a base legal de um produto apenas por leitura de um exercício. Tratamento real depende de contexto e de avaliação apropriada.

Registre eventos de segurança suficientes para investigar decisões e abuso, sem gravar senhas, tokens, dados de pagamento ou conteúdo pessoal desnecessário. Proteja os próprios logs, restrinja acesso e defina retenção. Observabilidade deve ajudar a descobrir falhas, sem criar uma cópia ampla dos dados protegidos.

**Exemplo:** um log registra identificador interno de requisição, rota, decisão de autorização e resultado de limite, mas não o token bearer nem o corpo completo com dados do cliente.

**Erro comum:** guardar tudo “para depurar depois” ou concluir que uma coleta é legal porque existe uma caixa de consentimento.

**Checagem:** para cada campo pessoal, a equipe consegue explicar a finalidade técnica, a necessidade, o acesso e a retenção sem armazenar valores desnecessários no log?

