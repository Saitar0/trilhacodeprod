---
arquivo_id: "f9-46-2-m01-fluxo-contrato-e-ambiente-local"
parent_key: "46.2"
tipo_arquivo: "project_milestone"
ordem: 1
itens_origem: ["M01"]
titulo_marco: "Entrega 1 — Fluxo, contrato e ambiente local"
---


### Entrega 1 — Fluxo, contrato e ambiente local
Desenhe o caminho da operação no Trilho A até o efeito assíncrono. Registre a decisão de separar o serviço, a chave/id do evento, versão do contrato, campos, significado, produtor, consumidor, ownership dos dados e comportamento esperado em caso de atraso. Prepare o ambiente local com RabbitMQ e dependências necessárias, sem segredos no repositório. Documente como verificar que aplicação e broker estão prontos.


**Evidência:** ADR breve (contexto, decisão, alternativas e consequência), exemplo de evento sanitizado, diagrama e instruções de execução.

**Revisão:** rejeite payload que exponha segredo/dado pessoal sem necessidade; esclareça qualquer campo cujo significado ou autoridade não esteja definido. Se o fluxo exige resposta síncrona imediata, reavalie se mensageria é adequada.

