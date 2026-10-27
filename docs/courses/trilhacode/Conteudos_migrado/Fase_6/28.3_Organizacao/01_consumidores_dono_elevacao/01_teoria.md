---
arquivo_id: "f6-28-3-01-consumidores-dono-elevacao-01-teoria-md"
parent_key: "28.3"
tipo_arquivo: "theory"
assunto: "01_consumidores_dono_elevacao"
ordem: 1
itens_origem: ["## Microtópico 1 — Decida a partir dos consumidores e do ciclo de vida", "## Microtópico 2 — Eleve estado só até o proprietário necessário"]
---

## Microtópico 1 — Decida a partir dos consumidores e do ciclo de vida
Ao organizar estado, faça perguntas concretas: quem cria e altera esse valor? Quais componentes precisam lê-lo? Eles precisam permanecer sincronizados? O valor vem do servidor? Deve sobreviver a navegação, recarga ou compartilhamento por link? Pode ser calculado a partir de outros dados? As respostas ajudam a escolher onde mantê-lo sem aplicar uma regra rígida como “tudo local” ou “tudo global”.

Uma decisão útil começa pelo requisito observável. Um menu que só controla o próprio componente pode manter estado local. Se duas áreas independentes precisam coordenar qual painel está aberto, pode fazer sentido elevar o estado até o ancestral comum. Se o valor deve ser compartilhado em uma URL, a própria URL pode ser a fonte adequada. Dados remotos devem seguir a estratégia de consulta e cache definida para a aplicação, em vez de ganharem cópias globais sem sincronização.

| Pergunta | Indício para a decisão |
| --- | --- |
| Só um componente usa o valor? | Mantenha-o local e perto do comportamento |
| Componentes irmãos precisam mudar juntos? | Eleve ao ancestral comum mais próximo |
| Componentes distantes compartilham uma preferência de cliente? | Avalie Context ou uma store, conforme o escopo |
| O valor identifica uma busca ou vem da API? | Use URL/parâmetros e cache remoto de acordo com o contrato |
| O valor pode ser derivado de dados já disponíveis? | Calcule em vez de guardar uma segunda cópia |

## Microtópico 2 — Eleve estado só até o proprietário necessário
Quando componentes precisam permanecer coordenados, escolha um proprietário único e passe valor e ações aos consumidores. Em React, elevar estado ao ancestral comum permite que filhos leiam a mesma decisão e solicitem alterações ao proprietário. Isso é apropriado quando a relação de sincronização é real, como um acordeão em que apenas um painel pode estar aberto por vez.

Elevar tudo até a raiz da aplicação aumenta a distância entre a regra e os componentes que a usam. Mantenha o estado no nível mais próximo que atende a todos os consumidores. Se props atravessarem muitas camadas sem que os intermediários precisem do valor, Context pode reduzir essa passagem; se há uma necessidade duradoura de estado cliente entre áreas distantes, uma store pode ser adequada. Essas ferramentas resolvem problemas de distribuição, mas não tornam automaticamente cada dado global.

Componentes controlados e não controlados são escolhas de API. Quando o pai precisa coordenar o valor, recebe-o por props junto com um callback. Quando o estado é interno e não precisa ser coordenado, o componente pode gerenciá-lo sozinho. A escolha pode mudar quando os requisitos mudam, sem que uma das opções seja universalmente melhor.

