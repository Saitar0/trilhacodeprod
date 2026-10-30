# Relatório — Etapa 14H.3A: arquitetura da persistência editorial

**Estado:** arquitetura proposta, somente documental. Aguardando decisões humanas antes da 14H.3B.

## A. Resultado

Foi preparada uma arquitetura para futura persistência editorial isolada de blocos canônicos compartilhados, colocações e projetos. O desenho reutiliza os contratos de leitura das Etapas 14H.1 e 14H.2 e os padrões de transação, revisão imutável, hash e compare-and-swap demonstrados pelo repositório editorial da Etapa 14F.

**Nada foi implementado nesta etapa.** Não houve escrita ou conexão ao MongoDB, criação de coleções/índices, importação, publicação, integração com rotas, progresso, quizzes ou frontend. O bundle, as fontes curriculares e o contrato intermediário não foram alterados.

## B. Evidências observadas

- [TESTADO em etapas anteriores] O pacote declara 406 blocos canônicos compartilhados, 1.001 colocações e 284 assuntos consumidores distintos. As 1.001 colocações permanecem com `progress_scope: undecided`.
- [TESTADO em etapas anteriores] Há 15 projetos, 20 entregas e 36 marcos formais. O contrato distingue entregas de marcos, e registra opções de stack sem escolher uma.
- [IMPLEMENTADO offline] `shared_content.py` projeta cada bloco canônico uma vez e mantém as colocações como referências. `projects.py` projeta `ProjectSpec`, `ProjectDelivery` e `ProjectMilestone` sem convertê-los em conteúdo operacional.
- [IMPLEMENTADO, isolado] `activity_persistence.py` separa snapshots públicos e privados, versões imutáveis, eventos e heads; usa transação e controle de versão esperado.
- [TESTADO em ambiente descartável anterior] A Etapa 14F.2 testou MongoDB 9.0.2, replica set de um membro, transações, rollback, concorrência, índices e papéis distintos. Isso não prova failover nem configuração de produção.
- [IMPLEMENTADO] O progresso legado usa identidade interna de usuário/nó/bloco. O quiz usa usuário/quiz/versão. Submissões genéricas usam usuário/bloco/tentativa. Nenhum desses modelos inclui `placement_ref` ou a versão de um projeto.
- [PENDENTE] Não existe política aprovada para progresso compartilhado, audiência de rubricas, checklist persistente, evidências de projeto, avaliação de projeto, seleção de stack ou publicação de projetos.

## C. Recomendação arquitetural, ainda não aprovada

1. Manter uma identidade canônica por bloco e uma identidade independente por colocação. Não copiar payload do bloco nas colocações.
2. Versionar bloco, colocação e projeto em agregados distintos. Uma revisão de projeto deve conter entregas e marcos tipados como arrays separados, sem versões independentes de componentes até que exista necessidade aprovada.
3. Manter uma revisão editorial interna completa e uma apresentação pública derivada por allowlist positiva. Rubricas, critérios, checklists, soluções, feedback e notas permanecem privados até haver regra de audiência explícita.
4. Para relações de um projeto com blocos, guardar a referência curricular e, em uma futura versão publicável, uma referência imutável à versão exata do bloco. O bundle atual não fornece essas versões; nenhuma deve ser inventada.
5. Usar transação MongoDB para publicar conjuntamente revisão imutável, dados privados correspondentes, evento de auditoria, registro de idempotência e atualização do head por CAS.
6. Preservar conteúdo histórico. Ausência em um novo pacote não autoriza exclusão. A retirada de uma colocação seria uma nova revisão/tombstone, sem apagar o bloco canônico nem histórico de progresso.

> As seis recomendações acima são propostas de desenho. Nenhuma política de produto ou de operação foi aprovada por este relatório.

## D. Decisões e bloqueadores

A 14H.3B não deve iniciar escrita persistente até haver respostas explícitas na [matriz de decisões](MATRIZ_DECISOES_PERSISTENCIA_14H_3A.md). Bloqueiam especialmente: a identidade de progresso (incluindo tentativas de quiz compartilhado), audiência/revelação de material avaliativo, pinagem de versões, ciclo editorial/publicação, retenção/retirada de colocações, submissões/evidências, correção manual, checklist e escolha de stack.

O [plano 14H.3B](PLANO_IMPLEMENTACAO_14H_3B.md) define quais decisões bloqueiam cada incremento. A implementação futura deverá continuar em repositório isolado, sem rotas de aluno, importador ou progresso, a menos que uma autorização posterior amplie expressamente esse escopo.

## E. Validação desta etapa

- Branch `migracao-estrutura`; HEAD `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- Índice vazio. O worktree já continha 25 arquivos rastreados modificados e 148 não rastreados antes da criação destes documentos; foram preservados.
- SHA-256 do bundle antes/depois: `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.
- `git diff --quiet -- docs/courses/trilhacode/Conteudos` confirmou ausência de alterações nas fontes originais.
- `git diff --check` passou. O Git emitiu o aviso preexistente de conversão LF/CRLF para o JSON que já está modificado localmente; seu hash corresponde ao esperado.
- Não foram executados testes de banco, testes de aplicação ou comandos de migração; esta etapa alterou somente documentação.

## F. Arquivos desta etapa

- `docs/migracao/RELATORIO_ETAPA_14H_3A.md`
- `docs/migracao/ARQUITETURA_PERSISTENCIA_EDITORIAL_14H_3A.md`
- `docs/migracao/MATRIZ_DECISOES_PERSISTENCIA_14H_3A.md`
- `docs/migracao/PLANO_IMPLEMENTACAO_14H_3B.md`

Nenhum arquivo foi staged ou commitado. A Etapa 14H.3B não foi iniciada.

