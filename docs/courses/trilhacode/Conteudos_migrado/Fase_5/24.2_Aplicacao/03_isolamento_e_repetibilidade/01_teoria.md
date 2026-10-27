---
arquivo_id: "f5-24-2-03-isolamento-e-repetibilidade-01-teoria"
parent_key: "24.2"
tipo_arquivo: "theory"
assunto: "03_isolamento_e_repetibilidade"
ordem: 3
itens_origem: ["Microtópico 5 — Faça a suíte repetir sem depender da ordem"]
---

## Microtópico 5 — Faça a suíte repetir sem depender da ordem

Um teste repetível define seus dados, estado e dependências, executa a operação e encerra recursos mesmo quando há falha. Use identificadores únicos e conhecidos, ou um esquema por suíte/worker; restaure relógio, variáveis globais e dublês que alterou; feche aplicação e conexões no teardown. O cenário deve funcionar sozinho, em ordem diferente e em uma segunda execução.

Evite chamar serviço externo real em testes regulares quando um dublê ou servidor controlado atende à pergunta. Evite pausas fixas. Aguarde a resposta/condição de estado em vez de supor que uma operação termina após alguns milissegundos. Se um teste falha intermitentemente, preserve log e dados mínimos para localizar a dependência de tempo, rede, recurso compartilhado ou estado residual.

Ao avaliar uma falha, separe: a aplicação respondeu incorretamente; o banco ou serviço de teste não iniciou; a fixture não foi preparada; ou a limpeza contaminou outra execução. Essa distinção torna a suíte útil como feedback, e não somente um bloqueio difícil de diagnosticar.

