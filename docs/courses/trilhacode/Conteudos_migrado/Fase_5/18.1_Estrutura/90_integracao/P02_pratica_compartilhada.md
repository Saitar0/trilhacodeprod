---
arquivo_id: "f5-18-1-90-integracao-p02-pratica-compartilhada"
parent_key: "18.1"
tipo_arquivo: "practice"
assuntos: ["02_fluxo_de_requisicao_e_camadas", "03_validacao_em_runtime", "04_status_e_erros_http"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Separar camadas e validar uma criação
Desenhe o caminho de POST /tarefas desde o recebimento até a resposta. Separe middleware, controller, validação, serviço e persistência. Defina um schema de entrada com título obrigatório e limite explícito de tamanho; inclua um campo não permitido e descreva se será ignorado ou rejeitado. Aponte o status e o formato de erro para cada falha.

**Dica:** middleware não deve conhecer todas as regras de domínio. Validação de estrutura acontece antes do serviço; a regra de negócio continua protegida no serviço e, quando aplicável, no banco.

