---
arquivo_id: "f5-17-2-90-integracao-p02-pratica-compartilhada"
parent_key: "17.2"
tipo_arquivo: "practice"
assuntos: ["02_stack_traces_e_erros_assincronos", "03_logs_contexto_seguro"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Seguir uma falha assíncrona
Monte ou use uma função que leia configuração ou arquivo e cuja Promise possa rejeitar quando a entrada não existe. Observe a stack trace, siga a rejeição até a camada que decide a resposta e acrescente contexto sem apagar a causa original. Explique qual parte pode responder ao usuário e qual detalhe deve permanecer apenas no diagnóstico.

**Dica:** diferencie mensagem útil para quem usa a aplicação da informação técnica necessária para depuração. Não devolva caminho local, stack trace ou segredo na resposta pública.

