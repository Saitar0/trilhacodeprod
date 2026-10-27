---
arquivo_id: "f9-46-3-m03-falhas-retry-dlq-e-idempotencia"
parent_key: "46.3"
tipo_arquivo: "project_milestone"
ordem: 3
itens_origem: ["M03"]
titulo_marco: "Entrega 3 — Falhas, retry, DLQ e idempotência"
---


### Entrega 3 — Falhas, retry, DLQ e idempotência
Adicione chave idempotente persistida de forma atômica com o efeito sempre que possível. Confirme a mensagem depois do commit do efeito. Configure tentativas finitas, backoff adequado, classificação de falhas e rota de DLQ. Documente quem pode autorizar redrive, como se corrige a causa, como se preserva o event ID e como se evita apagar o histórico. Escolha a durabilidade e garantia de dead lettering compatíveis com o ambiente e a versão do broker; declare as limitações.


**Evidência:** testes automatizados ou roteiro reproduzível para duplicata, queda entre efeito e ack, erro transitório, mensagem inválida e redrive, com contagem e estado observado.

**Revisão:** demonstre que duplicidade permanece segura sob concorrência, que não há loop infinito e que o ack não precede a persistência. publisher confirm não substitui a idempotência do consumidor.

