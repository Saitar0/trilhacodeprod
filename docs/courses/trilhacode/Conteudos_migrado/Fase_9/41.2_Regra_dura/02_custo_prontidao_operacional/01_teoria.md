---
arquivo_id: "f9-41-2-02-custo-prontidao-operacional-01-teoria"
parent_key: "41.2"
tipo_arquivo: "theory"
assunto: "02_custo_prontidao_operacional"
ordem: 2
itens_origem: ["### 2. Custo total e prontidão operacional"]
---


### 2. Custo total e prontidão operacional
Uma fronteira de processo adiciona rede, latência, indisponibilidade parcial, autenticação serviço a serviço, deploy e rollback independentes, contratos versionados, telemetria distribuída, filas ou chamadas remotas, gestão de dados e plantão. Se o novo serviço compartilha tabelas e transações com o monólito, a separação de código pode não produzir autonomia e ainda introduzir dual writes e dependência de rede.

Antes de extrair, confirme quem assume:
- build, deploy, configuração, segredos, migrações e rollback;
- SLO/alertas, logs, métricas, traces e resposta a incidentes;
- compatibilidade de API/eventos e evolução dos consumidores;
- propriedade de dados, backup, retenção, privacidade e reconciliação;
- capacidade, custo, segurança e suporte fora do horário comercial.

Uma equipe pequena pode não ter capacidade para manter várias pilhas operacionais. “Gerenciado” reduz parte da infraestrutura, mas não remove a responsabilidade pelo serviço e seus efeitos de negócio. Um monólito modular com limites internos, testes de contrato entre módulos e propriedade clara pode oferecer organização suficiente com menos partes móveis.

