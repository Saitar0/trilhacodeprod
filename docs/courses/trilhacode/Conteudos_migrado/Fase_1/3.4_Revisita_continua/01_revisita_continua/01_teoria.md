---
arquivo_id: "f1-3-4-01-revisita-continua-01-teoria"
parent_key: "3.4"
tipo_arquivo: "theory"
assunto: "01_revisita_continua"
ordem: 1
itens_origem: ["Versionar como hábito", "Revisar o histórico e as branches", "README e escrita técnica em inglês"]
---

## Teoria

### Versionar como hábito
Git é útil quando o histórico registra unidades de trabalho compreensíveis. Depois de uma mudança que forma um estado coerente, revise `git status` e o diff; então registre o que deseja preservar. Commits pequenos e explicativos ajudam a encontrar quando e por que algo mudou. Não é necessário criar um commit para cada tecla, e mudanças incompletas podem permanecer em uma branch de trabalho até fazer sentido registrá-las.

### Revisar o histórico e as branches
Revisitar `git log --oneline --graph --decorate` e `git status` ajuda a identificar commits vagos, branches antigas e mudanças não registradas. Antes de apagar uma branch, confirme se o trabalho foi integrado ou preservado em outro lugar. Branches locais e remotas são referências separadas; apagar uma não implica apagar a outra.

Uma revisão periódica também pode verificar README, `.gitignore`, issues abertas e arquivos gerados. Se um segredo aparecer, trate a credencial primeiro; editar o README ou apagar um arquivo da branch atual não apaga cópias do histórico.

### README e escrita técnica em inglês
O README de um repositório de estudos deve responder: qual é o propósito, como navegar, quais ferramentas são necessárias e como reproduzir os exercícios. Para cumprir o objetivo deste módulo, escreva o README, títulos dos commits de estudo e issues em inglês simples. Use frases curtas e vocabulário consistente. Inglês claro é mais útil que tradução literal rebuscada; preserve nomes oficiais de comandos e tecnologias.

