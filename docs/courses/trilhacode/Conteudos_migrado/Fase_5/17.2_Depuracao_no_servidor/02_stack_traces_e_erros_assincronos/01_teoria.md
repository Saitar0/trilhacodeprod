---
arquivo_id: "f5-17-2-02-stack-traces-e-erros-assincronos-01-teoria"
parent_key: "17.2"
tipo_arquivo: "theory"
assunto: "02_stack_traces_e_erros_assincronos"
ordem: 2
itens_origem: ["3. Stack traces e falhas assíncronas"]
---

### 3. Stack traces e falhas assíncronas
Uma stack trace registra frames que ajudam a localizar onde um erro foi criado e por quais chamadas síncronas chegou ali. Comece pela mensagem e pelo primeiro frame relevante da aplicação, mas não assuma que esse frame é automaticamente a causa: siga os valores e chamadas até encontrar a condição incorreta. Código de dependências, wrappers e limites assíncronos podem aparecer no trace; mapas de origem ajudam quando o código executado foi transformado.

Em Promises, preserve a rejeição e encaminhe-a para uma camada capaz de tratá-la. Se adicionar contexto e criar um novo Error, preserve a causa original quando possível, em vez de descartá-la. Diferencie erro esperado de entrada, falha externa e defeito inesperado; cada caso pede uma resposta e um nível de registro diferentes. [Node.js — Errors](https://nodejs.org/api/errors.html).

