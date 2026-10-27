---
arquivo_id: "f9-40-3-90-integracao-p03-pratica"
parent_key: "40.3"
tipo_arquivo: "practice"
assuntos: ["01_modelar_problema_antes_escolha", "02_entrega_falhas_duplicatas", "03_ordem_escala_replay", "04_operacao_custo_decisao"]
ordem: 3
itens_origem: ["P03"]
---


### Atividade 3 — Recomendação operacional e econômica
**Contexto:** equipe pequena prevê 2 milhões de mensagens/mês, payload médio de 8 KiB, dois consumidores, picos de 10 vezes a média e retenção desejada de 7 dias. Valores são premissas didáticas, não cotação.

**Instruções:** escolha uma tecnologia para um caso de tarefas sem replay e outra para eventos que precisam replay. Esboce cálculo de volume de dados, chamadas/consumo, retenção e transferência; liste o que precisa ser cotado na região escolhida; estime tarefas de operação mensal (atualização, capacidade, alertas, segurança, recuperação); proponha teste de pico e indisponibilidade. Se uma premissa não puder ser traduzida diretamente ao modelo do serviço, registre a diferença.

**Entrega:** decisão de uma página com premissas, faixa ou drivers de custo, responsabilidade operacional, riscos, plano de teste e gatilhos para reavaliar a escolha. Não é necessário inventar uma tarifa.

**Dica gradual:** calcule mensagens e bytes antes de escolher; separe custo do serviço de custo de pessoas; use páginas oficiais de preço e limites para preencher os fatores atuais.

