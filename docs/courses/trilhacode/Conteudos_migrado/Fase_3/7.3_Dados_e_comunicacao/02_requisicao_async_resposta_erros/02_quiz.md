---
arquivo_id: "f3-7-3-02-requisicao-async-resposta-erros-02-quiz"
parent_key: "7.3"
tipo_arquivo: "quiz"
assunto: "02_requisicao_async_resposta_erros"
ordem: 2
itens_origem: ["Q1", "Q2", "Q3", "Q4", "Q5"]
---

## Verificação — quiz
1. `fetch` recebeu uma resposta HTTP 404. O que geralmente acontece? **A)** A Promise de `fetch` é rejeitada automaticamente. **B)** Ela resolve com um `Response` cujo `ok` é falso. **C)** O navegador transforma o corpo em JSON. **D)** A política CORS é desligada. 

2. O que `await` faz numa função `async`? **A)** Espera a Promise e deixa a função continuar com o resultado ou tratar a rejeição. **B)** Bloqueia toda a interface até a rede responder. **C)** Converte a resposta automaticamente para JSON válido. **D)** Altera o status HTTP para sucesso. 

3. Qual é a ordem apropriada para obter uma lista JSON e identificar uma resposta HTTP malsucedida? **A)** verificar `response.ok`, depois ler o corpo com `response.json()`. **B)** chamar `response.json()` antes de aguardar `fetch`. **C)** assumir que todo `Response` tem status 200. **D)** chamar `JSON.stringify(response)`. 

4. O servidor respondeu HTTP 200, mas `response.json()` falhou. Qual hipótese descreve melhor o problema? **A)** O corpo não pôde ser interpretado como JSON. **B)** O servidor não respondeu. **C)** O status 200 significa que o conteúdo é sempre JSON válido. **D)** É obrigatoriamente erro de CORS. 

5. Uma aplicação não consegue ler uma resposta de outra origem por CORS. Onde deve ser configurada a permissão necessária? **A)** No servidor/API que responde, usando os headers adequados. **B)** Em `JSON.parse` no cliente. **C)** Em uma regra CSS. **D)** Em `mode: "no-cors"` para manter o corpo legível. 

