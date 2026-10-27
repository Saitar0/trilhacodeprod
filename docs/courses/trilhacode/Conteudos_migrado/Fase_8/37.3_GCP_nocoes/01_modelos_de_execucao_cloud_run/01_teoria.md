---
arquivo_id: "f8-37-3-01-modelos-de-execucao-cloud-run-01-teoria-md"
parent_key: "37.3"
tipo_arquivo: "theory"
assunto: "01_modelos_de_execucao_cloud_run"
ordem: 1
itens_origem: ["### Microtópico 1 — Escolher como executar código no Cloud Run"]
---

### Microtópico 1 — Escolher como executar código no Cloud Run

Cloud Run é uma plataforma gerenciada para executar código em containers. A escolha começa pelo formato do trabalho:

- **Service:** recebe requisições HTTP em um endpoint e pode também integrar-se a eventos. É apropriado para APIs, aplicações web e serviços que respondem a chamadas.
- **Job:** executa tarefas que começam, processam trabalho e terminam; pode ser iniciado manualmente ou por uma agenda/orquestração.
- **Worker pool:** executa trabalho em segundo plano que não depende de receber uma requisição HTTP, como consumidores de filas. O modelo de escala e os gatilhos não são os mesmos de um service.
- **Instance:** atende alguns casos que pedem um ambiente de execução singleton e de longa duração.

A plataforma reduz a necessidade de administrar servidores ou cluster, mas não elimina decisões sobre aplicação, identidade, rede, configuração, limites, observabilidade e persistência. O filesystem gravável local da instância é temporário; dados que precisam sobreviver devem ir para armazenamento apropriado. Não escolha apenas pela palavra “serverless”: confira o contrato de execução e o comportamento de escala do recurso específico.

Cloud Run pode resolver problemas semelhantes aos tratados com containers gerenciados na AWS, inclusive ECS com Fargate em certos cenários. Isso não faz os serviços intercambiáveis. Runtime, forma de receber tráfego, integração, permissões, rede, escala e cobrança precisam ser comparados para o workload real.

