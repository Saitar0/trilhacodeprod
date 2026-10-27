---
arquivo_id: "f9-46-2-m02-publicacao-confiavel-e-rastreavel"
parent_key: "46.2"
tipo_arquivo: "project_milestone"
ordem: 2
itens_origem: ["M02"]
titulo_marco: "Entrega 2 — Publicação confiável e rastreável"
---


### Entrega 2 — Publicação confiável e rastreável
Implemente a mudança de negócio no Trilho A e a intenção de publicação com uma estratégia coerente. Para banco relacional, considere transactional outbox: gravação de estado e evento pendente na mesma transação, com um relay publicando depois. Outra abordagem pode ser usada se as garantias e falhas forem demonstradas. Configure publicação persistente, publisher confirms e verificação de roteamento de acordo com a biblioteca e a topologia adotadas. Confirms informam que o broker assumiu responsabilidade segundo sua configuração; não provam que o consumidor executou a regra de negócio.

Trate a perda de conexão e a confirmação ambígua: uma republicação pode gerar duplicata, então mantenha o mesmo event ID e espere idempotência no consumo. Registre métricas ou logs que permitam localizar publicação pendente, falha de publicação e mensagem correlacionada, sem registrar payload sensível.


**Evidência:** teste automatizado ou roteiro reprodutível cobrindo publicação normal, broker indisponível e reinício com item pendente, além de log/métrica correlacionável.

**Revisão:** confirme onde a transação do banco termina e como o relay marca o evento enviado. Explique por que publisher confirm e outbox resolvem fronteiras diferentes e por que pode haver publicação duplicada.

