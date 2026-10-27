---
arquivo_id: "f10-48-2-t03"
parent_key: "48.2"
tipo_arquivo: "theory"
assunto: "03_cancelamento_timeout_falhas"
ordem: 3
itens_origem: ["### 3. Cancelamento, timeout e falhas"]
---


### 3. Cancelamento, timeout e falhas
Quando a pessoa cancelar, atualize a interface imediatamente e sinalize cancelamento ao backend. O backend deve interromper o trabalho e propagar cancelamento ao SDK/provedor se essa capacidade existir, liberar recursos e encerrar o stream. Uma conexão encerrada no navegador não prova que o provedor interrompeu a geração nem que o uso deixa de ser cobrado; registre o que o sistema consegue confirmar.

Defina timeout para conexão e geração, máximo de saída, limite de entrada e concorrência. Trate rate limit, indisponibilidade, erro de autenticação e falha no meio do stream com respostas adequadas ao estágio: antes do primeiro fragmento, devolva erro estruturado; depois de começar, emita evento de erro/fim interrompido se o contrato permitir, sem fingir que a mensagem é completa. Retry automático após timeout pode gerar cobrança adicional ou duplicar uma ação; decida conforme idempotência e semântica da operação.

