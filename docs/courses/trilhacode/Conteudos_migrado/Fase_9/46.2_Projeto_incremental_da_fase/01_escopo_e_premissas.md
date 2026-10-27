---
arquivo_id: "f9-46-2-01-escopo-e-premissas"
parent_key: "46.2"
tipo_arquivo: "project_scope"
ordem: 0
itens_origem: ["Escopo e premissas"]
---


## Escopo e premissas
Parta do projeto acumulado no Trilho A e preserve sua stack principal. O evento deve representar um fato de negócio já ocorrido, não uma instrução técnica genérica como “atualizar tabela”. Escolha uma tarefa lateral que possa ser processada de forma assíncrona, como notificação ou geração de relatório, e explique por que tolera esse modelo. O serviço adicional deve ter um limite próprio e uma responsabilidade pequena; não crie serviços apenas para aumentar a contagem.

Defina antes da implementação quais dados podem circular no evento, quem é dono de cada dado, como identificar uma mensagem e que compatibilidade de contrato será mantida. Use dados fictícios no ambiente local e não publique segredos nem dados pessoais desnecessários. Fixe versões de dependências e documente como iniciar e encerrar o ambiente local.

