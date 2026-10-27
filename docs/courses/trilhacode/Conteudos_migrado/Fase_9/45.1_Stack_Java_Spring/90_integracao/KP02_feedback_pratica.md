---
arquivo_id: "f9-45-1-90-integracao-kp02-feedback-pratica"
parent_key: "45.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_persistencia_jpa_consultas", "03_testes_integracao_kafka"]
ordem: 2
itens_origem: ["P02"]
---


**Feedback para revisar:** para (a), um teste de unidade com repository substituído verifica a regra, mas não a consulta SQL; complemente com integração se o mapeamento/query for risco. Para (b), reconhecer redelivery é necessário; uma resposta adequada usa deduplicação/idempotência atômica ou outra estratégia explícita e não afirma que o ack, sozinho, resolve a consistência entre Kafka e banco.

**Construção opcional se Java/Spring for a stack escolhida:** API CRUD com Spring Boot, JPA e migração de banco, teste de controller e integração com Kafka local que demonstre redelivery idempotente. Registre as versões de Java e das ferramentas de build.

