---
arquivo_id: "f9-45-1-03-testes-integracao-kafka-f02-flashcards"
parent_key: "45.1"
tipo_arquivo: "flashcards"
assunto: "03_testes_integracao_kafka"
ordem: 2
itens_origem: ["FC03"]
---


- **Confirmar o offset do Kafka garante que banco e negócio ocorreram exatamente uma vez?** Não. Falhas entre gravação e confirmação podem provocar redelivery; o efeito precisa tolerar repetição e as fronteiras transacionais devem ser compreendidas.

