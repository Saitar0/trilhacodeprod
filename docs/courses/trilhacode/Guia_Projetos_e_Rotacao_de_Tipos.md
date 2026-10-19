---
title: "Guia de Projetos — Trilhos A e B e rotação de tipos"
aliases:
  - Guia de Projetos
  - Rotação de tipos de projeto
tags:
  - trilhas
  - projetos
  - estrutura-curricular
status: planejamento
---

# Guia de Projetos — Trilhos A e B e rotação de tipos

> [!abstract] Para que serve esta nota
> Os projetos seguem dois trilhos: um projeto principal que acumula de fase em fase (Trilho A) e projetos de fase com ideias rotativas (Trilho B). O resultado esperado é demonstrar as competências descritas na trilha; concluir os projetos não equivale, por si só, a experiência profissional ou a um nível de senioridade.

## 1. Os dois trilhos

| | Trilho A — Projeto principal | Trilho B — Projetos de fase |
|---|---|---|
| Quantidade | 1, evoluído da Fase 1 à Fase 10 | 1 por fase nas Fases 3, 4, 5, 6, 8, 9 e 10; a Fase 7 continua o Trilho A e seu projeto de infraestrutura é concluído na Fase 8 |
| Ideia | Escolhida na Fase 1; troca permitida uma vez, até o fim da Fase 4 (seção 2) | 3 ideias por projeto, com rotação de tipos (seções 3 a 5) |
| Objetivo | Mostrar evolução contínua e integração | Cobrir todos os tipos de problema |
| Conta para a cobertura de tipos | Não | Sim |
| Onde está | Submódulos "Projeto incremental da fase" | Submódulos "Projeto de fase (Trilho B)" |

## 2. Trilho A — escolha na Fase 1

No submódulo 3.5 a pessoa escolhe **uma** destas ideias e a mantém até o projeto final (52.1). Como a escolha é feita com pouca informação, é permitido trocá-la **uma única vez**, até o fim da Fase 4, registrando o motivo no README. Todas comportam as entregas das dez fases e uma funcionalidade de IA ao final.

1. **Gestor de tarefas e projetos em equipe**
2. **Loja virtual**
3. **Base de conhecimento colaborativa**

O Trilho A exercita cada ideia em largura; o Trilho B isola o problema difícil de um tipo. As duas coisas não são redundantes, mas há afinidade natural:

| Ideia do Trilho A | Tipos com mais afinidade |
|---|---|
| Gestor de tarefas e projetos em equipe | T2 (multiempresa) e T3 (tempo real) |
| Loja virtual | T1 (transacional) |
| Base de conhecimento colaborativa | T4 (conteúdo e busca) e T6 (IA) |

Ao fazer no Trilho B um tipo afim ao do Trilho A, use a ideia do guia (ingressos, clínicas, receitas...) e não reimplemente o projeto principal; o Trilho A pode reaproveitar as soluções depois.

## 3. Os seis tipos de projeto

Os tipos são definidos pelo **problema técnico difícil** que forçam, e não pelo assunto do negócio.

| Tipo | Ideia | Problema difícil que força |
|---|---|---|
| **T1 — Transacional** | Venda de ingressos com estoque limitado | Consistência de estoque, pagamento duplicado e idempotência |
| **T2 — SaaS multiempresa** | Agendamento para várias clínicas | Isolamento de dados por empresa e autorização por papel |
| **T3 — Tempo real e colaboração** | Quadro colaborativo ou votação ao vivo | Atualização ao vivo e estado compartilhado entre clientes |
| **T4 — Conteúdo, feed e busca** | Catálogo de receitas com busca e feed | Paginação, filtros, índices, cache e latência |
| **T5 — Dados e processamento assíncrono** | Importador de vendas e relatórios | Ingestão em volume, jobs, filas e reprocessamento seguro |
| **T6 — IA aplicada** | Assistente de documentos | RAG, function calling, custo, avaliação e segurança |

## 4. Regras de rotação

1. Cada projeto de fase mostra **3 ideias**, de tipos diferentes.
2. Um tipo já concluído é **repetido**: continua visível, mas é **opcional** e **não conta** para a cobertura.
3. Para concluir o projeto, a pessoa escolhe **1 entre as ideias não repetidas**.
4. As 3 ideias exibidas são os 3 tipos **pendentes** com menos fases restantes de disponibilidade (empate: ordem T1 a T6). Se houver menos de 3 pendentes, completam-se as vagas com tipos repetidos (opcionais).
5. Um tipo só pode ser escolhido nas fases em que está disponível (seção 5).
6. O curso só é concluído com **os 6 tipos feitos pelo menos uma vez** (tabela da seção 8).
7. A Fase 9 costuma ser o projeto **livre**: se todos os tipos de T1 a T5 já foram feitos, a pessoa escolhe qualquer ideia para aprofundar, sem custo para a cobertura.
8. A Fase 10 oferece sempre T6, que é obrigatório. Tipos ainda pendentes viram projetos de recuperação, na versão da Fase 9.
9. **A versão da fase é autocontida.** Como cada fase usa uma ideia diferente, a versão de um tipo feito pela primeira vez numa fase tardia inclui a **base mínima** das camadas anteriores (tabela abaixo), e não só a camada nova. A versão da fase descreve a camada nova.
10. **Escopo mínimo.** Cada projeto do Trilho B é uma fatia vertical que exercita o problema difícil do tipo e termina quando o critério do tipo é demonstrado por teste, medição ou cenário reproduzível. Telas, estilo e funcionalidades laterais ficam fora. As faixas iniciais estão em [[Estimativa_de_Carga_Horaria|Estimativa de carga horária]] e nos submódulos de projeto das fases; elas pressupõem esse escopo mínimo e serão calibradas com dados de estudantes.
11. **Tipo na primeira fase em que aparece.** Quando a ordem permitir, prefira fazer um tipo na primeira fase em que ele está disponível, pois a versão é a mais curta.

| Primeira vez do tipo na fase | Base mínima a incluir |
|---|---|
| 3 (T1, T2 ou T4) | Protótipo de navegador com HTML/CSS/JavaScript e JSON local; sem exigir banco ou API persistente |
| 4 | Nenhuma: a versão já é o modelo de dados |
| 5 | Esquema mínimo no PostgreSQL (2 a 4 tabelas) com migrations e uma API simples |
| 6 | API real da Fase 5, consumida pela interface (sem banco) |
| 8 | A base da Fase 5, mais Dockerfile, pipeline e a métrica pedida |
| 9 | A base da Fase 5, mais fila, retry, DLQ, idempotência e ADR (Compose local, sem exigir a nuvem) |

> [!tip] Por que a conta fecha
> Há 5 tipos base (T1 a T5) para 6 projetos de fase nas Fases 3, 4, 5, 6, 8 e 9. Enquanto houver tipos pendentes, cada projeto pode concluir um tipo novo; a vaga excedente permite aprofundamento. T3 só fica disponível a partir da Fase 5 e tem prioridade pela regra 4. A Fase 10 é uma entrega adicional: T6 é obrigatório e os tipos pendentes podem ser recuperados.

## 5. Quais projetos e quais tipos estão disponíveis

| Fase | Submódulo | Entrega da fase | Tipos disponíveis |
|---|---|---|---|
| 3 | 8.6 | Protótipo sem framework, dados em JSON local, acessível, responsivo e publicado | T1, T2, T4 |
| 4 | 16.3 | Modelo relacional no PostgreSQL, migrations, relatórios e uma consulta medida | T1, T2, T4, T5 |
| 5 | 24.4 | API autenticada no PostgreSQL com testes de rotas e serviços | T1 a T5 |
| 6 | 31.5 | Interface React tipada sobre a API real, com os cinco estados e testes | T1, T2, T4, T5 |
| 8 | 39.3 | Versão implantada com Docker, pipeline e observabilidade básica | T1 a T5 |
| 9 | 46.3 | Variante com fila, retry, DLQ, idempotência e ADR | T1 a T5 |
| 10 | 52.2 | Funcionalidade de IA com avaliação e modelo de ameaças | T6 (e recuperação) |

Na Fase 10 as 3 ideias são variações de T6: assistente de documentos de uma empresa, copiloto de atendimento ou busca semântica no catálogo.

## 6. Versão da fase de cada ideia

### T1 — Venda de ingressos com estoque limitado
- **Fase 3:** carrinho e checkout simulados no navegador, com validação de formulário e total calculado.
- **Fase 4:** eventos, ingressos, pedidos e pagamentos com constraints e uma transação que impede vender além do estoque.
- **Fase 5:** API de pedidos com autenticação, reserva de estoque e pagamento simulado com chave de idempotência, testada.
- **Fase 6:** fluxo de compra em React com os cinco estados de interface e testes do checkout.
- **Fase 8:** API implantada com pipeline e métrica de pedidos por minuto.
- **Fase 9:** pagamento processado por fila, com retry, DLQ e idempotência.

### T2 — Agendamento para várias clínicas
- **Fase 3:** painel com papéis simulados (administrador e atendente) que mostra ou esconde ações.
- **Fase 4:** tenants, usuários, papéis e agenda; consultas sempre filtradas por tenant; constraint contra conflito de horário.
- **Fase 5:** autorização por tenant e papel, com teste que prova que um tenant não acessa dados de outro.
- **Fase 6:** telas por papel em React com rotas protegidas.
- **Fase 8:** variáveis por ambiente, staging e rollback.
- **Fase 9:** lembretes de agendamento processados por fila.

### T3 — Quadro colaborativo ou votação ao vivo
- **Fase 5:** WebSocket ou SSE transmitindo atualizações a vários clientes, com autenticação na conexão, reconexão e teste com dois clientes (conteúdo do 18.3).
- **Fase 8:** implantação com proxy e HTTPS mantendo as conexões, e métrica de conexões abertas.
- **Fase 9:** difusão entre várias instâncias via mensageria, tratando mensagens duplicadas.

### T4 — Catálogo de receitas com busca e feed
- **Fase 3:** listagem com filtros, ordenação e paginação sobre JSON, acessível.
- **Fase 4:** consultas filtradas e paginadas com índices justificados por EXPLAIN e cache Redis em uma consulta lenta.
- **Fase 5:** endpoints paginados e filtrados, com versionamento e documentação OpenAPI.
- **Fase 6:** lista paginada com TanStack Query e virtualização com medição antes e depois.
- **Fase 8:** dashboard de latência por endpoint.
- **Fase 9:** projeção de busca (tabela denormalizada ou índice dedicado) atualizada de forma assíncrona por fila.

### T5 — Importador de vendas e relatórios
- **Fase 4:** carga de CSV grande no PostgreSQL com constraints e relatório por agregação, com consulta medida.
- **Fase 5:** upload e processamento por job com stream, com status consultável pela API.
- **Fase 6:** relatório em React com filtros, tabela paginada e os cinco estados de interface.
- **Fase 8:** job em container com logs estruturados e métrica de duração e falhas.
- **Fase 9:** ingestão por fila com retry, DLQ e idempotência (reimportar não duplica).

### T6 — Assistente de documentos
- **Fase 10:** ingestão de documentos, recuperação com citação da fonte, function calling com autorização, avaliação em conjunto de casos, custo e latência medidos e modelo de ameaças curto.

## 7. Exemplo de percurso

| Fase | Oferecidas | Escolhida | Pendentes depois |
|---|---|---|---|
| 3 | T1, T2, T4 | T4 | T1, T2, T3, T5, T6 |
| 4 | T1, T2, T5 | T5 | T1, T2, T3, T6 |
| 5 | T1, T3 (e um repetido, opcional) | T3 | T1, T6 |
| 6 | T1, T2 (e um repetido, opcional) | T2 | T1, T6 |
| 8 | T1 (e dois repetidos, opcionais) | T1 | T6 |
| 9 | Todas repetidas | Livre | T6 |
| 10 | T6 | T6 | nenhum |

No exemplo, o T1 só é feito na Fase 8; pela regra 9, a versão dele inclui a base mínima da Fase 5 (esquema e API simples com reserva de estoque e idempotência) além do Dockerfile, do pipeline e da métrica.

## 8. Tabela de cobertura

Marque o tipo quando o critério de conclusão do projeto da fase for atingido.

| Tipo | Feito? | Fase | Repositório |
|---|---|---|---|
| T1 — Transacional | [ ] | | |
| T2 — SaaS multiempresa | [ ] | | |
| T3 — Tempo real e colaboração | [ ] | | |
| T4 — Conteúdo, feed e busca | [ ] | | |
| T5 — Dados e processamento assíncrono | [ ] | | |
| T6 — IA aplicada | [ ] | | |

## 9. Critério de conclusão do curso

- Projeto principal (Trilho A) entregue em todas as fases e fechado no 52.1.
- Os 6 tipos do Trilho B concluídos.
- Cada projeto com README, testes e decisões registradas, o que alimenta o portfólio do 53.1.
