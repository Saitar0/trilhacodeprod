---
arquivo_id: "f5-21-1-01-coesao-responsabilidades-01-teoria"
parent_key: "21.1"
tipo_arquivo: "theory"
assunto: "01_coesao_responsabilidades"
ordem: 1
itens_origem: ["Microtópico 1 — Coesão: responsabilidades que pertencem juntas"]
---

## Microtópico 1 — Coesão: responsabilidades que pertencem juntas
Coesão descreve o quanto os elementos de um módulo trabalham para um propósito compreensível. Uma função ou módulo coeso reúne comportamento que faz sentido mudar junto. Isso não exige que cada classe tenha somente um método ou que toda ação do sistema ganhe um serviço próprio. O sinal útil é se o módulo mantém uma ideia clara e se suas mudanças têm uma razão reconhecível.

Uma função que recebe HTTP, interpreta formato, aplica uma regra de negócio, grava dados, envia e-mail e monta HTML pode estar acumulando razões de mudança diferentes. Mas a solução não é cortar o código em pedaços sem nome ou contrato. Primeiro identifique qual comportamento pertence à regra, qual adapta entrada/saída e qual conversa com uma dependência externa.

**Exemplo:** uma operação de cancelamento decide se um pedido pode ser cancelado. A regra pode ser expressa sem depender do formato da requisição HTTP; o controller converte a requisição e a resposta; uma porta de saída pode enviar uma notificação se a regra exige esse efeito.

**Erro comum:** inferir baixa coesão apenas pelo tamanho do arquivo ou pela presença de vários métodos. Um módulo pequeno pode misturar razões de mudança; um módulo maior pode continuar coeso se seus comportamentos servem ao mesmo propósito.

**Checagem:** quais mudanças independentes fariam este módulo mudar? Se cada alteração exige editar trechos sem relação e conhecer detalhes diferentes, investigue uma separação útil.

