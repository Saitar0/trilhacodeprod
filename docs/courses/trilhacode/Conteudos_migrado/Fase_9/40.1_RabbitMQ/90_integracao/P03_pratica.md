---
arquivo_id: "f9-40-1-90-integracao-p03-pratica"
parent_key: "40.1"
tipo_arquivo: "practice"
assuntos: ["02_confirmacoes_ack_idempotencia", "04_dead_letter_recuperacao"]
ordem: 3
itens_origem: ["P03"]
---


### Atividade 3 — Definir retry, DLQ e triagem
Classifique três falhas sintéticas: timeout temporário no serviço dependente; payload inválido; consumer que cai repetidamente. Defina quais falhas podem ser tentadas novamente, o limite/atraso, quando rejeitar sem requeue, DLX/queue de destino, alerta e procedimento de triagem. Consulte o tipo e a versão de fila do ambiente para registrar a garantia de dead-letter realmente habilitada.

**Entrega:** tabela de erro → ação/retries → destino final; configuração do broker ou um diagrama executável; procedimento para corrigir e reprocessar uma mensagem sem duplicar efeito.

**Critérios de aceite:** erros permanentes não entram em requeue imediato infinito; existe limite e destino DLQ com binding; alertas consideram tamanho/idade; mecanismo de entrega DLX está explicitamente identificado como at-most-once ou at-least-once conforme a configuração real; reprocessamento é idempotente.

