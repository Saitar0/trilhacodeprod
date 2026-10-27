---
arquivo_id: "f5-17-1-02-promises-async-await-01-teoria"
parent_key: "17.1"
tipo_arquivo: "theory"
assunto: "02_promises_async_await"
ordem: 2
itens_origem: ["3. Promises e async/await"]
---

### 3. Promises e async/await
Uma Promise representa um resultado que pode chegar no futuro. async/await facilita escrever a continuação desse trabalho, mas não cria thread nem torna código CPU-bound paralelo. Ao aguardar uma Promise, a função assíncrona suspende sua continuação; outras tarefas elegíveis podem progredir. Rejeições precisam ser tratadas com try/catch ou propagadas para quem chama.

Use Promise.all quando operações independentes puderem começar juntas e todas forem necessárias ao resultado. Isso não reduz automaticamente o custo de cada operação e pode aumentar a pressão sobre um serviço externo se usado sem limite. Operações dependentes devem aguardar a etapa anterior.

