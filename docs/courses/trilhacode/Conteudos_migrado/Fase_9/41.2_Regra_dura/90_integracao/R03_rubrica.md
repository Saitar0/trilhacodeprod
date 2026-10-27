---
arquivo_id: "f9-41-2-90-integracao-r03-rubrica"
parent_key: "41.2"
tipo_arquivo: "rubric"
assuntos: ["02_custo_prontidao_operacional", "04_extracao_incremental_reversao"]
ordem: 3
itens_origem: ["P03"]
escala_rubrica: "0–2 por critério; cinco critérios; total 10; demais condições literais."
---


**Rubrica (0–2 cada, total 10):** rollout tem etapas reversíveis; dados têm fonte da verdade; duplicatas/efeito externo são tratados; telemetria e gates são mensuráveis; rollback inclui eventos e efeitos persistidos. Aceite com pelo menos 8 pontos e nenhuma etapa que dependa de “voltar o código” para desfazer efeito externo.

**Erro comum:** retirar o fluxo antigo logo depois do primeiro deploy ou supor que rollback de aplicação apaga mensagens e e-mails já enviados.

