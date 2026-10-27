---
arquivo_id: "f9-45-1-03-testes-integracao-kafka-01-teoria"
parent_key: "45.1"
tipo_arquivo: "theory"
assunto: "03_testes_integracao_kafka"
ordem: 3
itens_origem: ["### 3. Testes e integração com Kafka"]
---


### 3. Testes e integração com Kafka
Escolha o teste pela fronteira que precisa verificar. Um teste de controller com contexto reduzido pode validar rota, serialização e status HTTP; teste de service com dependências substituídas examina decisões de negócio; teste de integração com banco verifica mapeamento, consulta e transação reais. Um mock do repository é útil para isolar comportamento, mas não prova SQL, configuração do ORM ou compatibilidade com o banco de produção.

Spring for Apache Kafka fornece abstrações para publicar mensagens e receber eventos. No consumo, a aplicação precisa definir quando confirma o offset, como trata falhas e redelivery, e o que acontece após esgotar retries; política de erro pode encaminhar mensagens para uma dead-letter topic, conforme a configuração. Se o efeito no banco ocorrer e o processo falhar antes da confirmação do offset, o evento pode ser entregue novamente. Projete o efeito para ser idempotente, por exemplo registrando um identificador de evento processado junto da alteração de negócio, com restrição atômica. Confirmação do broker, transação Kafka e gravação no banco não formam automaticamente uma única transação de negócio de ponta a ponta.

**Se esta for a stack escolhida:** reclassifique a unidade como obrigatória ou média e faça uma trilha prática de Java, tipos, exceções, coleções e Maven/Gradle antes de construir uma API CRUD Spring Boot. Inclua migrações, testes adequados às fronteiras e, se Kafka fizer parte do projeto, um consumidor com política explícita de retry e deduplicação. Consulte as matrizes oficiais de compatibilidade e fixe versões de Java, Spring Boot, Spring Data e Kafka no projeto; elas mudam ao longo do tempo.

