---
arquivo_id: "f9-45-1-90-integracao-p02-pratica"
parent_key: "45.1"
tipo_arquivo: "practice"
assuntos: ["02_persistencia_jpa_consultas", "03_testes_integracao_kafka"]
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Escolher testes e proteger o consumo
Considere duas situações: (a) um método de service calcula o total de um pedido e usa um repository; (b) um consumidor Kafka grava uma alteração no banco e só depois confirma o offset. Para cada situação, escolha o teste que dá evidência adequada. Na segunda, descreva o que acontece se o processo cair depois da gravação e antes da confirmação e proponha uma proteção contra duplicidade.

**Entregável:** uma matriz com situação, risco, teste e evidência esperada, mais um parágrafo descrevendo a falha e a proteção para Kafka.

