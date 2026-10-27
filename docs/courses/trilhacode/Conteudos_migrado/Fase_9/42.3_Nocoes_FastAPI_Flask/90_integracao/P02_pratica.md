---
arquivo_id: "f9-42-3-90-integracao-p02-pratica"
parent_key: "42.3"
tipo_arquivo: "practice"
assuntos: ["02_convencoes_composicao_custo", "03_sync_async_operacao"]
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Revise uma afirmação sobre async
**Contexto:** numa revisão, alguém afirma: “Vou converter todas as rotas Flask para `async def`; assim cada requisição libera o worker e consigo executar tarefas de fundo sem Celery”. O serviço faz chamadas bloqueantes a banco e envia e-mails.

**Instruções:** marque cada parte da afirmação como correta, incorreta ou incompleta; identifique protocolo e comportamento do worker; proponha o que verificar para decidir entre Flask, FastAPI ou manter o framework; indique como fazer o envio de e-mail de forma durável e como medir a capacidade.

**Entrega:** revisão de até 200 palavras com dois riscos, um desenho alternativo e três medidas/testes de carga ou integração.

**Dica gradual:** consulte o modelo WSGI do Flask; se a biblioteca chamada não oferece I/O awaitable, `async def` não remove o bloqueio; uma view não é uma fila persistente.

