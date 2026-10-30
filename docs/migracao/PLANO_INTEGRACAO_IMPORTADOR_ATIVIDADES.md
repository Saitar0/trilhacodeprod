# Plano de integração do importador — atividades tipadas

**Estado atual:** somente repositório editorial isolado. Nenhuma atividade do pacote foi gravada, publicada ou importada. Este plano não autoriza os passos futuros.

## Estado real e bloqueadores

- O runtime existente publica quizzes objetivos imutáveis em `quiz_versions`, usa o catálogo ativo e guarda tentativas em `quiz_progress`.
- `TypedActivityDraftStore` grava rascunhos/revisões em quatro coleções distintas (`typed_activity_public_versions`, `typed_activity_private_versions`, `typed_activity_version_events` e `typed_activity_heads`) e não está conectado a rotas nem à inicialização da aplicação. Revisões subsequentes exigem `expected_version_id` e avançam o head com compare-and-swap na transação.
- Não se deve manter um segundo catálogo operacional. `quiz_versions` continua sendo a fonte operacional; as novas coleções servem apenas a preparação editorial enquanto isso for necessário.
- Não há correspondência aprovada que ligue cada atividade tipada/question ID a um node/quiz operacional existente. Um snapshot autorizado é necessário antes de sincronizar.
- O ambiente atual não tem URI explícita de replica set descartável, Docker daemon ou `mongod`; atomicidade, índices e concorrência reais ainda não estão homologados.
- 358 questões com gabarito continuam sem conversão objetiva adequada; cinco questões R1–R5 continuam não pontuadas. Não publicar essas atividades.
- Respostas abertas, discursivas, associação e ordenação não possuem avaliadores operacionais definidos.

## Sequência futura proposta

### 1. Homologar infraestrutura de teste descartável

Provisionar fora desta etapa um replica set MongoDB de teste, de um membro, com porta dedicada, URI explícita, banco aleatório por execução e confirmação de que o processo é descartável. O teste `test_typed_activity_persistence_mongodb.py` confere host local, porta, nome de replica set e `hello` antes de qualquer escrita. Obter versão/topologia e testar índices, transações, rollback, repetição e concorrência. Não reaproveitar `MONGO_URL` de desenvolvimento.

### 2. Reconciliar identidade e duplicação

Com snapshot read-only autorizado, comparar `activity_ref`, versões e `curriculum_ref` com nodes, `quiz_versions`, tentativas e relações existentes. Produzir conflitos sem alterações. Definir por decisão explícita como atividade curricular vira quiz agrupado, pois 14E modela pergunta individual e runtime opera um quiz de um node com várias questões.

### 3. Endurecer acesso privado

Definir credenciais/roles Mongo para separar leitura pública e leitura privada. Verificar que o usuário do runtime público não consegue consultar `typed_activity_private_versions`; somente serviço administrativo/corretor autorizado pode ler gabaritos. Provar com testes de integração e auditoria de logs sem dados de correção.

### 4. Revisar conteúdo e status

Revisores autorizados podem decidir `draft → pending_review → structurally_validated → publishable` mediante eventos de auditoria separados. Não permitir mudança de conteúdo no mesmo `version_id`. `published` somente pela rota de publicação existente depois de gates aprovados; a camada 14F não executa essa transição. Os 143 candidatos não se tornam publicáveis pela validação estrutural.

### 5. Adaptar questões aprovadas ao runtime

Após decisões editoriais e reconciliação, converter unicamente múltipla escolha com alternativas e chave inequívocas para o contrato aceito por `_question_snapshot`/serviço de quiz. Adaptar para `quiz_versions` preservando IDs, ordem, resposta privada, explicação, proveniência, versão e hash. Não publicar short answer/discursiva/associação/ordenação até existir avaliador e política aprovados.

### 6. Dry-run e revisão humana

Gerar plano por operação: criar, idempotente/inalterado, novo snapshot, conflito, bloqueado ou pendente. Não propor exclusões por ausência. A revisão deve incluir diffs público/privado, identidade e impactos em histórico. O hash do pacote curricular e a revisão do manifesto são entradas imutáveis da execução.

### 7. Publicação experimental separada

Somente após autorização específica, usar rota administrativa existente com permissão `content.publish`, em ambiente descartável e com feature flag desligada para alunos. Reutilizar a política atual: três tentativas, 70%, melhor nota, histórico imutável, gabarito após terceira tentativa. Verificar endpoints públicos, históricos, recuperação, progresso e pré-requisitos.

### 8. Ativação/rollout

Exige homologação separada de produto e operações. Confirmar topology/backup/restore, RBAC, observabilidade, feature flag, rollback e compatibilidade frontend. A Etapa 14F não altera a flag nem define rollout.

## Critérios de aceite para futura integração

1. `quiz_versions` permanece fonte única dos snapshots avaliativos publicados.
2. O mesmo `activity_ref` não gera registros operacionais duplicados.
3. Gabaritos permanecem privados em banco, APIs, histórico, logs e bundle público.
4. Transações e índices são provados no replica set descartável.
5. Reexecução idempotente mantém IDs e versões anteriores.
6. Conteúdo diferente vira nova versão, sem recalcular tentativas.
7. Relações curriculares continuam com semântica atual; sem inferir `quiz_passed`.
8. Nenhuma avaliação incompleta ou decisão pendente é publicada.
9. Nenhuma ausência do pacote remove documento, relação ou progresso.
10. Importação e ativação recebem homologação específica antes de execução.
