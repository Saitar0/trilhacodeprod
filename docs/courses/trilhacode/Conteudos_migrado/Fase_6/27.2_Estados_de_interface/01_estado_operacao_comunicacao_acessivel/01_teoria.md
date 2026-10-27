---
arquivo_id: "f6-27-2-01-estado-operacao-comunicacao-acessivel-01-teoria-md"
parent_key: "27.2"
tipo_arquivo: "theory"
assunto: "01_estado_operacao_comunicacao_acessivel"
ordem: 1
itens_origem: ["## Microtópico 1 — Modele o estado dos dados e da operação", "## Microtópico 5 — Torne mudanças perceptíveis e verificáveis"]
---

## Microtópico 1 — Modele o estado dos dados e da operação
“A tela carregou” não descreve todos os cenários. Há pelo menos duas perguntas: **que dados estão disponíveis?** e **o que a rede está fazendo agora?** Uma requisição inicial sem dados, uma resposta válida vazia e uma atualização em segundo plano com dados anteriores não devem ser representadas como o mesmo estado.

Uma máquina simples pode descrever a disponibilidade dos dados: `pending → success | error`. Dentro de `success`, a coleção pode conter itens ou estar vazia. A atividade de rede é uma dimensão separada: `fetching`, `paused` ou `idle`. Por isso, uma consulta pode estar em `success` e continuar buscando dados em segundo plano. Em aplicações próprias, modele essas dimensões com nomes claros e transições válidas; evite vários booleanos independentes sem regras, pois combinações como “vazio e erro” podem produzir uma tela contraditória.

| Situação | Dados disponíveis | Atividade | Apresentação esperada |
| --- | --- | --- | --- |
| Primeira consulta | Ainda não | Buscando | Indicador de carregamento inicial |
| Resposta com itens | Sim, atuais | Ociosa | Lista de resultados |
| Resposta válida sem itens | Sim, coleção vazia | Ociosa | Estado vazio com orientação útil |
| Falha inicial | Não | Ociosa ou encerrada | Erro com ação apropriada |
| Atualização em segundo plano | Sim, possivelmente anteriores | Buscando | Manter conteúdo e indicar atualização |
| Falha ao atualizar | Sim, possivelmente desatualizados | Encerrada | Manter dados úteis e explicar a falha de atualização |

O estado deve vir da operação e do contrato da API, não de inferências frágeis como “a lista não existe, então está carregando”. Se a aplicação usa uma biblioteca de consulta, aprenda como ela distingue disponibilidade de dados e atividade de rede antes de mapear flags para a interface.

## Microtópico 5 — Torne mudanças perceptíveis e verificáveis
Estados dinâmicos devem ser compreensíveis sem depender apenas de cor, animação ou posição. Associe textos claros aos indicadores; preserve foco durante atualizações que não exigem mudança de contexto; e garanta que ações como tentar novamente sejam operáveis por teclado. Para uma região que recebe resultados de forma assíncrona, `role="status"` pode anunciar uma atualização não urgente sem mover o foco. Use anúncios concisos e evite relatar cada detalhe repetidamente. `aria-busy="true"` pode indicar que uma região está sendo atualizada e deve voltar a falso quando a atualização terminar.

Uma revisão visual e com tecnologias assistivas deve cobrir primeira carga, resultado, vazio, falha inicial, atualização de dados existentes, falha de atualização e retry. Torne esses cenários reproduzíveis com respostas controladas, latência artificial ou mocks. Registre o resultado esperado e o que comprova cada transição; não dependa de uma falha de rede aleatória para demonstrar o comportamento.

