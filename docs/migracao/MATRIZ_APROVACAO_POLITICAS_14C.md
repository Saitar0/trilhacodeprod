# Matriz de aprovação de políticas — Etapa 14C

**Estado geral: aguardando decisão humana.** Esta matriz separa recomendação técnica de decisão editorial/de produto. Nenhuma proposta abaixo foi aplicada ao pacote, ao JSON, ao banco ou ao currículo.

| Tema | Evidência atual | Recomendação técnica | Decisão necessária | Estado |
|---|---|---|---|---|
| Progresso de conteúdo compartilhado | 406 conteúdos canônicos, 1.001 colocações; todos os `progress_scope` estão `undecided`. | Considerar progresso por colocação/contexto para evitar conclusão cruzada entre assuntos; ver análise de alternativas no [contrato de conteúdo compartilhado](CONTRATO_CONTEUDO_COMPARTILHADO.md). | Aprovar progresso global, por colocação ou modelo híbrido. | Pendente; nenhum scope alterado. |
| Cinco perguntas R1–R5 sem gabarito | Projeto 16.3; não há chave associada no pacote. | Preservar como revisão não pontuada até decisão; eventual revisão humana exige fluxo separado. | Confirmar revisão formativa sem nota ou aprovar avaliação humana e seus critérios documentados. | Pendente; sem resposta, nota ou critério criado. |
| Modelo de projetos | 15 projetos, 20 entregas, 36 marcos formais e componentes tipados no pacote. | Usar entidade versionada de projeto e componentes distintos para entrega/marco, apenas quando constarem na fonte. | Aprovar o contrato e os requisitos de acesso/publicação/progresso antes da extensão de backend/frontend. | Pendente; nenhum modelo implementado. |
| 34 relações rotuladas explicitamente como pré-requisito | O pacote marca `kind=prerequisite`, `enforced=true`; as fontes usam rótulo de pré-requisito sem declarar aprovação de quiz. | Considerar `content_completed`, sujeito à aprovação; não inferir `quiz_passed`. | Aprovar individualmente a classificação proposta na [matriz das relações](MATRIZ_DECISOES_CURRICULARES.md). | Pendente; relações não convertidas. |
| Relação “pré-requisito/revisita” | Uma das 35 combina os dois termos; não esclarece se a revisita bloqueia acesso. | Manter sem subtipo até esclarecimento, em vez de aplicar o candidato usado nas demais. | Decidir entre dependência de conteúdo e relação informativa de revisita. | Pendente editorial. |
| 11 referências sem destino | O dry-run registra 11 blocos com `target=null`, identificados por ID e arquivo na [matriz das relações e referências](MATRIZ_DECISOES_CURRICULARES.md). | Preservar como texto/referência pendente; nunca inventar destino. | Confirmar o destino, se houver evidência, ou aprovar que continuem referências textuais sem navegação. | Pendente editorial. |

## Gate para implementação

Somente depois das aprovações acima, preparar a especificação executável correspondente e validar um novo plano offline. A aprovação destas políticas não autorizaria por si só importação, publicação de quizzes, alteração de progresso ou escrita no MongoDB; cada etapa operacional precisará de homologação própria.
