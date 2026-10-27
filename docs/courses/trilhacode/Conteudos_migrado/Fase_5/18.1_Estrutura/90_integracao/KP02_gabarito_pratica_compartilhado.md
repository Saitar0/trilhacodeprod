---
arquivo_id: "f5-18-1-90-integracao-kp02-gabarito-pratica-compartilhado"
parent_key: "18.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_fluxo_de_requisicao_e_camadas", "03_validacao_em_runtime", "04_status_e_erros_http"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** parser e middleware de contexto executam antes da rota; controller envia o body para o validador; se válido, chama serviço de criação; serviço aplica regras e persiste; controller responde 201 com representação/identificador. Entrada malformada ou campos inválidos geram resposta documentada, como 400; conflito de domínio pode ser 409. Um middleware de erro final converte falhas inesperadas em resposta segura e registra detalhes internamente.

