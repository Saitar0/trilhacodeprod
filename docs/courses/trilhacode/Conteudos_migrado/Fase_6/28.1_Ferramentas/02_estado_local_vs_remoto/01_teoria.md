---
arquivo_id: "f6-28-1-02-estado-local-vs-remoto-01-teoria-md"
parent_key: "28.1"
tipo_arquivo: "theory"
assunto: "02_estado_local_vs_remoto"
ordem: 2
itens_origem: ["## Microtópico 3 — Separe estado de interface e estado remoto"]
---

## Microtópico 3 — Separe estado de interface e estado remoto
**Zustand** mantém estado do cliente que vários componentes precisam compartilhar, como um painel aberto, uma seleção temporária ou uma preferência de interface. A store contém estado e ações; componentes podem selecionar somente o valor de que precisam. Evite transformar toda variável local em estado global: isso aumenta os acoplamentos e torna mais difícil descobrir quem pode alterar um valor.

**TanStack Query** organiza dados assíncronos que vêm de uma fonte externa: executa consultas, mantém cache por chave, acompanha atualizações e oferece mecanismos para sincronizar o cache depois de mutações. A chave deve identificar os dados consultados e incluir as variáveis que mudam a resposta, como identificador, página e filtro. Se a função da consulta usa um parâmetro que altera o resultado, ele precisa participar da identidade da consulta.

Uma regra prática: preferência de ordenação exclusivamente visual pode pertencer ao estado do cliente; uma ordenação que altera a consulta também faz parte dos parâmetros da consulta remota. O mesmo valor pode ter representação em mais de uma camada por motivos distintos, mas precisa haver uma fonte de verdade definida e uma regra de sincronização. Copiar a resposta da API para uma store sem essa política cria caches concorrentes e risco de dados divergentes.

| Necessidade | Onde começar | Motivo |
| --- | --- | --- |
| Campo de busca usado só neste formulário | Estado local do React | Escopo pequeno, sem compartilhamento necessário |
| Painel lateral aberto em várias telas | Store de cliente, se o compartilhamento for real | Estado de interface compartilhado |
| Lista carregada de uma API com cache e atualização | TanStack Query | Estado remoto tem ciclo de busca e sincronização próprio |
| Preferência que deve sobreviver à navegação e ser compartilhável | URL ou persistência deliberada | O requisito define o ciclo de vida e o compartilhamento |
| Projeto sem necessidade que as ferramentas resolvam | Ferramentas existentes | Dependência nova também tem custo de manutenção |

