---
arquivo_id: "f5-18-3-90-integracao-p02-pratica-compartilhada"
parent_key: "18.3"
tipo_arquivo: "practice"
assuntos: ["03_seguranca_de_canais", "04_estado_compartilhado_e_concorrencia"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Implementar canal autenticado para um recurso
Crie uma pequena funcionalidade de progresso compartilhado ou estado de tarefa para dois clientes. Autentique o usuário, confira autorização no recurso antes da inscrição, valide mensagens de entrada e propague uma mudança a ambos. Inclua ID ou versão no evento e mantenha uma leitura HTTP para obter estado autoritativo ao iniciar ou recuperar.

**Dica:** teste com duas sessões distintas: uma permitida e outra sem acesso. A inscrição em sala precisa passar pela mesma regra de autorização aplicada às leituras e alterações HTTP.

