---
arquivo_id: "f10-48-2-t04"
parent_key: "48.2"
tipo_arquivo: "theory"
assunto: "04_observabilidade_privacidade_custo"
ordem: 4
itens_origem: ["### 4. Observabilidade, privacidade e custo"]
---


### 4. Observabilidade, privacidade e custo
Meça o tempo até a primeira parte visível, o tempo total, encerramentos por estado, erros por classe, volume de tokens/unidade tarifada, requisições concorrentes e cancelamentos. Se possível, compare tempos do provedor e do caminho até o navegador para separar geração de buffering da infraestrutura. Use IDs de correlação e métricas agregadas; não registre prompts e respostas sensíveis por padrão.

Aplique rate limit e limites de custo no backend, por usuário/fluxo e também globalmente quando apropriado. Conte concorrência, tamanho de entrada/saída, chamadas de ferramenta e repetição. Um limite somente no navegador pode ser contornado. Revise custo e qualidade juntos: reduzir saída ou chamadas pode reduzir latência e custo, desde que os critérios da tarefa continuem atendidos. As tarifas e formas de cobrança precisam ser consultadas na documentação vigente.

