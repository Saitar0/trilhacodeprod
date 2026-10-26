---
arquivo_id: "f1-2-2-03-logs-01-teoria"
parent_key: "2.2"
tipo_arquivo: "theory"
assunto: "03_logs"
ordem: 3
itens_origem: ["Logs"]
---

### Logs
Um **log** é um registro de eventos produzido por um sistema ou aplicação. Ele pode incluir data/hora, componente, nível e mensagem. Para investigar, delimite qual programa falhou e em que horário; procure primeiro a mensagem de erro e linhas próximas. Logs podem conter dados pessoais, tokens ou detalhes internos, portanto não os publique sem revisão.

`tail` mostra as últimas linhas de um arquivo; `tail -f arquivo.log` acompanha novas linhas em algumas implementações. `grep "ERROR" arquivo.log` seleciona linhas correspondentes ao padrão. `grep` pode receber saída por pipe, por exemplo `tail -f app.log | grep --line-buffered ERROR`, mas opções variam entre implementações.

