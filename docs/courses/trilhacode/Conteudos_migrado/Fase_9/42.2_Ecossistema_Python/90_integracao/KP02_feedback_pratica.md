---
arquivo_id: "f9-42-2-90-integracao-kp02-feedback-pratica"
parent_key: "42.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_celery_tarefas_fora_requisicao", "02_pytest_fixtures_integracao", "03_poetry_dependencias_distribuicao"]
ordem: 2
itens_origem: ["P02"]
---


**Feedback de referência:** chave idempotente estável para a cobrança; teste unitário cobre política de retry com respostas simuladas; teste em sandbox cobre integração com provedor de teste e não repete cobranças reais; aplicativo registra/usa o lockfile no CI, enquanto consumidor de biblioteca resolve suas próprias versões dentro das restrições publicadas.

**Erro comum:** presumir que “o teste passou” significa que o serviço externo processou uma única cobrança.

