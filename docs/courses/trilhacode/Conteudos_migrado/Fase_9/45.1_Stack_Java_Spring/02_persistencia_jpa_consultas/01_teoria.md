---
arquivo_id: "f9-45-1-02-persistencia-jpa-consultas-01-teoria"
parent_key: "45.1"
tipo_arquivo: "theory"
assunto: "02_persistencia_jpa_consultas"
ordem: 2
itens_origem: ["### 2. Persistência: especificação, implementação e consultas"]
---


### 2. Persistência: especificação, implementação e consultas
Jakarta Persistence (JPA) define contratos para mapeamento objeto-relacional e operações de persistência; Hibernate é uma implementação popular. Spring Data JPA adiciona abstrações de repository e pode derivar consultas a partir de nomes de métodos ou executar consultas declaradas. A conveniência reduz código repetitivo, mas não elimina a necessidade de entender SQL, índices, cardinalidade e o comportamento da consulta gerada.

Entidades e relacionamentos têm ciclo de vida e estratégia de carregamento. Acessar uma coleção lazy fora do contexto de persistência pode falhar; percorrer relações em uma lista pode gerar muitas consultas (N+1). Analise a consulta e o volume esperado, use paginação quando a lista puder crescer e confirme o comportamento com banco de teste quando ele for parte do risco. Delimite transações em torno de uma operação de negócio coerente; não presuma que cada método de repository, isoladamente, dá atomicidade ao fluxo inteiro.

