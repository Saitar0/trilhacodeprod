---
arquivo_id: "f9-46-2-m03-consumidor-resiliente-retry-e-dlq"
parent_key: "46.2"
tipo_arquivo: "project_milestone"
ordem: 3
itens_origem: ["M03"]
titulo_marco: "Entrega 3 — Consumidor resiliente, retry e DLQ"
---


### Entrega 3 — Consumidor resiliente, retry e DLQ
Implemente o consumidor para validar versão e conteúdo antes do efeito. Faça o efeito de negócio e o registro de deduplicação de forma atômica na persistência sempre que possível. Confirme a mensagem manualmente somente depois do efeito persistido. Se o processo cair após gravar e antes do ack, a mensagem pode voltar; a segunda entrega não pode repetir o efeito.

Classifique falhas transitórias e permanentes. Faça retry limitado com espera progressiva apropriada ao caso, sem ciclo infinito de requeue imediato. Encaminhe falha permanente ou esgotamento ao mecanismo de DLQ configurado. Registre motivo, event ID, contagem de tentativas e horário, com acesso e retenção adequados. Defina triagem e redrive manual ou controlado; ao reprocessar, preserve identidade e trilha de auditoria. Não presuma que configurar um DLX torna qualquer topologia imune a perda: escolha a garantia adequada à versão e tipo de fila e documente a decisão.


**Evidência:** testes ou roteiro reprodutível de sucesso, duplicata, queda entre commit e ack, falha transitória, poison message e redrive, com observação dos estados e contadores.

**Revisão:** verificar que o ack sucede o commit; deduplicação está protegida contra concorrência; os retries são finitos; a mensagem na DLQ pode ser diagnosticada; redrive não apaga a trilha.

