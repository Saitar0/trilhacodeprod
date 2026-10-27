---
arquivo_id: "f3-7-3-02-requisicao-async-resposta-erros-03-gabarito-quiz"
parent_key: "7.3"
tipo_arquivo: "answer_key"
assunto: "02_requisicao_async_resposta_erros"
ordem: 2
itens_origem: ["Q1", "Q2", "Q3", "Q4", "Q5"]
---

**Resposta: B.** Status HTTP de erro não rejeita, por si só, a Promise de `fetch`; o código deve verificar `ok` ou `status`.
**Resposta: A.** A pausa afeta a continuação da função assíncrona, não o navegador inteiro; conversão e status precisam ser tratados separadamente.
**Resposta: A.** Primeiro confira o status HTTP; a leitura do corpo é outra operação assíncrona e também pode falhar.
**Resposta: A.** A resposta chegou com sucesso HTTP, mas o corpo pode estar vazio, malformado ou em outro formato.
**Resposta: A.** O servidor autoriza origens; `no-cors` não dá acesso ao corpo ou status da resposta opaca.
