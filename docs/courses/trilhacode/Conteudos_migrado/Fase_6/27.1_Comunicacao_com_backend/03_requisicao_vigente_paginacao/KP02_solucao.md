---
arquivo_id: "f6-27-1-03-requisicao-vigente-paginacao-kp02-solucao-md"
parent_key: "27.1"
tipo_arquivo: "answer_key_pratica"
assunto: "03_requisicao_vigente_paginacao"
ordem: 2
itens_origem: ["P02"]
---

**Solução de referência:** Effect depende do filtro e da página, cria controller, inicia GET e só grava a resposta da execução atual; cleanup aborta ou marca como ignorada. A segunda busca representa os dados ativos; resposta atrasada não altera resultado nem estado de erro. Requisição de escrita acionada por usuário não deve ser tratada como leitura cancelável.

