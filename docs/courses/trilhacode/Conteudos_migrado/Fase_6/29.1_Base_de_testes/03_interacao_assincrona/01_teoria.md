---
arquivo_id: "f6-29-1-03-interacao-assincrona-01-teoria-md"
parent_key: "29.1"
tipo_arquivo: "theory"
assunto: "03_interacao_assincrona"
ordem: 3
itens_origem: ["## Microtópico 3 — Consulte, interaja e aguarde corretamente"]
---

## Microtópico 3 — Consulte, interaja e aguarde corretamente
Escolha a consulta conforme a expectativa temporal:

- `getBy...` é apropriada quando o elemento já deve estar presente; falha imediatamente se não encontrar ou se a consulta for ambígua.
- `queryBy...` é útil para verificar ausência sem lançar erro quando nada é encontrado.
- `findBy...` espera até que um elemento apareça ou que o tempo limite seja atingido, sendo útil para atualizações assíncronas.

Para uma ação de usuário, use uma API de interação como `user-event` ou a API recomendada pelo ambiente de teste escolhido. Interagir pelo botão, teclado ou campo exercita mais do fluxo do que chamar diretamente uma função interna. Faça o teste assíncrono quando a interação ou o resultado depender de uma Promise. Use `waitFor` para uma expectativa que precisa ser repetida enquanto a interface atualiza; mantenha dentro dele uma assertion, sem colocar a ação de usuário ali, porque a função pode executar mais de uma vez.

Os testes devem verificar um resultado observável após o evento. Não basta confirmar que um mock foi chamado se o contrato importante também é a mensagem, navegação ou atualização que a pessoa vê. Assertions de chamadas são úteis quando a chamada é parte do contrato entre componentes, mas não substituem a verificação da resposta da interface.

