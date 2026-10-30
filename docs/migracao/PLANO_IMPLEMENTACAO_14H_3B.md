# Plano incremental — Etapa 14H.3B

**Status:** plano futuro. Nenhuma tarefa abaixo foi iniciada ou aprovada para execução. A 14H.3B depende da aprovação explícita das decisões indicadas na matriz 14H.3A.

## G0 — Gate de produto e congelamento do contrato

- **Objetivo:** registrar decisões aprovadas e confirmar que o bundle e os contratos fonte permanecem imutáveis.
- **Possíveis arquivos:** novo registro de decisão em `docs/migracao/`; schemas dentro de `backend/curriculum_contract/` somente com autorização da 14H.3B.
- **Dependências/bloqueios:** D01–D18 conforme o domínio; nenhuma implementação de escrita até resolver as decisões aplicáveis.
- **Testes/evidência:** validação offline do bundle SHA, schemas e mapa de decisão aprovado.
- **Aceite:** nenhuma recomendação pendente tratada como padrão; escopo explícito sem rotas/importador/progresso.
- **Rollback:** nenhum dado é escrito; reverter somente alterações documentais autorizadas, preservando fonte.

## G1 — Contratos de persistência isolados

- **Objetivo:** definir Pydantic estrito para `block head/revision`, `placement head/revision`, `project head/revision`, eventos e idempotência, com identidade curricular e Mongo interna separadas.
- **Arquivos potenciais:** novos módulos dentro de `backend/curriculum_contract/` e testes unitários dedicados. Não assumir nomes até inventariar o pacote.
- **Dependências:** D01–D05; decisões de audiência para declarar payloads público/privado; D08 não precisa ser resolvida para preservar `undecided`, mas bloqueia qualquer regra operacional de progresso.
- **Testes:** extras proibidos; refs únicas; tipo/ownership; hashing canônico; serialização round-trip; versões; blocos privados fora de serializer seguro; conteúdo de projeto com entregas/marcos sem conversões.
- **Aceite:** todos os 406 blocos/1.001 colocações/15 projetos representáveis sem perda e sem valores inferidos; `progress_scope` preservado exatamente.
- **Rollback:** sem banco; retirar apenas schema/teste deste incremento, mantendo contratos de origem intactos.

## G2 — Repositório canônico e revisão de bloco

- **Objetivo:** persistir draft/revisão de bloco compartilhado de forma isolada, sem publicação nem aluno.
- **Arquivos potenciais:** novo módulo isolado em `backend/curriculum_contract/`; testes unitários e de repositório. Não modificar `shared_content.py` além de uma interface de leitura aprovada.
- **Dependências:** G1, D01/D02/D04/D06/D07/D16. Decisão de pinagem é necessária antes de aceitar referências versionadas.
- **Operação:** chave de idempotência + hash; transação com revisão segura, privado opcional, evento e CAS do head; resultados `created/unchanged/conflict/unknown`, sem exclusões.
- **Testes:** replay idêntico/divergente, stale CAS, referência privada, falhas antes/depois das escritas, retry de resultado desconhecido.
- **Aceite:** revisão imutável; pares público/privado consistentes; não há role pública com acesso ao store; sem conexão a rotas.
- **Rollback:** abort de transação antes do commit; após commit, correção por nova revisão, nunca delete.

## G3 — Repositório de colocações

- **Objetivo:** persistir `placement_ref -> block_ref + subject_ref + order + progress_scope`, separado do conteúdo canônico.
- **Arquivos potenciais:** módulo isolado de persistência de placements e testes; nenhuma mudança em `services/progress.py` ou `learning.py`.
- **Dependências:** G1/G2, D01/D02/D05/D08/D10/D16/D18; referência `subject_ref` precisa resolver sem título/ordem. A escolha de progresso pode continuar pendente desde que código nenhum a interprete.
- **Testes:** bloco compartilhado existente; target `topic`; unicidade de placement, par ativo e ordem contextual; scopes preservados; concorrência de reordenação; retirada sem apagar bloco/histórico.
- **Aceite:** nenhuma cópia de payload; todas as 1.001 referências reconciliadas ou listadas como bloqueadas; zero escrita em progresso.
- **Rollback:** apontador/head volta somente via operação aprovada e auditada; nenhuma exclusão física de histórico.

## G4 — Repositório de projetos agregados

- **Objetivo:** guardar revisão imutável de `ProjectSpec`, com arrays distintos de entregas e marcos, opções e referências pinadas quando disponíveis.
- **Arquivos potenciais:** módulo de persistência de projetos e testes; reutilizar `projects.py` para validação/leitura offline, sem mudar `submissions.py`.
- **Dependências:** G1, D03–D07, D11, D15/D16. Sem decisão de audiência, revisões permanecem internas e nenhum snapshot de aluno é produzido.
- **Testes:** 15 projetos, 20 entregas, 36 marcos; projeto sem filhos; referências de aceite; stacks nulas/vazias preservadas; stale CAS; nenhuma submissão/pontuação criada.
- **Aceite:** entrega não vira marco; marco não vira entrega; não se criam componentes; versão antiga relida com conteúdo semanticamente idêntico.
- **Rollback:** nova revisão compensatória; sem mutação ou remoção da revisão anterior.

## G5 — Índices e migração de schema, somente em banco descartável

- **Objetivo:** criar e verificar índices de heads/revisões, placements e idempotência.
- **Arquivos potenciais:** migração específica e função de preflight isolada, após aprovação. Não alterar `backend/indexes.py` operacional nesta etapa sem autorização.
- **Dependências:** G1–G4 e D05/D10/D16. Snapshot autorizado para checar dados preexistentes antes de qualquer índice em ambiente real.
- **Testes:** MongoDB descartável com URI/porta/dbpath explícitos; criação idempotente; duplicatas detectadas antes do índice; papéis distintos.
- **Aceite:** índices reais conferidos no servidor descartável e diagnóstico seguro de dados duplicados; nenhuma migração real.
- **Rollback:** remover somente índices/DB descartável criado pelo teste; em ambiente real, não executar sem autorização, backup e plano próprio.

## G6 — Transações, concorrência e falhas

- **Objetivo:** comprovar atomicidade de revisão + partes privadas + evento + operação + head CAS.
- **Arquivos potenciais:** repositórios de G2–G4 e testes de integração Mongo isolados.
- **Dependências:** G5, D17; confirmação de sessões na mesma transação.
- **Testes:** falha depois de cada escrita, antes de CAS, commit desconhecido, duas e três revisões concorrentes sobre a mesma base, replay da mesma chave, chave divergente, restart/reconciliação, leitores durante atualização.
- **Aceite:** no máximo um concorrente divergente vence; sem documentos órfãos; resultado de commit desconhecido não dispara nova revisão; evidência do estado persistido, não só do retorno.
- **Rollback:** abort confirmado no teste; falha incerta resolvida por operação idempotente. Teste de replica set de um membro não será apresentado como prova de failover.

## G7 — RBAC e auditoria de privacidade

- **Objetivo:** limitar leitura de revisão privada e verificar allowlists em todos os serializadores.
- **Arquivos potenciais:** schemas/serializadores editoriais isolados e configuração de papéis só para teste; nada em APIs existentes.
- **Dependências:** D06/D07/D14/D15; aprovação de papéis/grants.
- **Testes:** credencial pública negada nas coleções internas/privadas; editor sem permissão avaliativa não lê gabarito; permissão interna mínima; mass assignment; logs, erros, dumps, OpenAPI e respostas sem dados privados.
- **Aceite:** acesso público futuro somente por projeção separada autorizada; nenhuma rota pública é criada nesta subetapa.
- **Rollback:** remover somente usuários/roles/banco do ambiente descartável; grants de produção não fazem parte do plano.

## G8 — Auditoria offline de cobertura

- **Objetivo:** comparar contrato/persistência de teste com pacote para detectar perda e colisão, sem importação curricular.
- **Arquivos potenciais:** validador offline e relatório de auditoria; nunca escrever no bundle.
- **Dependências:** G1–G7 e as decisões semânticas relevantes.
- **Testes:** 406/1.001/284 e 15/20/36, hashes e refs, blocos privados, ordens, `progress_scope`, variantes; execução determinística em duas ordens.
- **Aceite:** cada entidade tem destino proposto ou bloqueio rastreável; sem criar projeto, marco, resposta, audiência ou progresso.
- **Rollback:** relatório descartável/regerável; não alterar dados de origem.

## Fora do escopo da 14H.3B

Importação do bundle, bulk upsert, publicação de projetos, páginas/componentes, submissões de aluno, upload de arquivo, correção manual operacional, alteração do progresso, migração de progresso antigo, alteração de tentativas de quiz, política de stack por aluno ou rota API pública. Cada item requer escopo e aprovação posteriores.

## Gate de encerramento da 14H.3B

A 14H.3B só poderá ser homologada quando os requisitos de persistência autorizados tiverem evidência de transação, CAS, idempotência, RBAC, isolamento privado, cobertura/round-trip, integridade de índices e ausência de regressão, em Mongo descartável. A homologação não autoriza por si só importação, publicação, integração de frontend, mudança de progresso ou conexão a banco de produção.

