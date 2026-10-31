# PoC de gerações editoriais imutáveis

## Escopo

Esta prova de conceito fica em `backend/services/editorial_generations_poc.py` e
usa somente coleções `poc_*` recebidas por injeção. Não é chamada por rotas,
`publish_track`, `restore_version`, serviços de conteúdo ou leitores atuais.
Não altera `track_publications`, `version_chunks`, `published_activity_version_id`
nem índices de produção. A entrada é um snapshot já capturado e serializado em
JSON; a PoC não torna consistente a leitura das coleções editoriais mutáveis.

## Coleções e contratos

| Coleção | Conteúdo | Escritas da PoC |
|---|---|---|
| `poc_editorial_generations` | Registro mutável da operação, estado, writer, fencing token, lease e intenção de selagem | Insert e CAS/update condicionado |
| `poc_editorial_generation_chunks` | Partes append-only identificadas por geração, fencing token e sequência | Insert; nunca update/delete |
| `poc_editorial_generation_manifests` | Manifesto final selado, hashes, referências exatas de chunks e metadados de validação | Insert idempotente; nunca update/delete |
| `poc_editorial_generation_heads` | Ponteiro experimental por trilha, revisão e recibos de seleção | Upsert inicial e CAS de um documento |

Índices PoC: operação única por `(track_id, operation_id)`, chunks únicos por
`(generation_id, fencing_token, seq)`, manifesto único por geração e um head por
trilha. `ensure_poc_indexes` só opera quando chamado explicitamente com um banco
injetado; não faz parte de `ensure_indexes`. É pré-condição chamar esse setup
antes de usar `begin`; a PoC não cria índices implicitamente no construtor.

## Selagem, fencing e recuperação

1. `begin` canonicaliza/valida o snapshot, fixa o hash da operação e registra a
   geração como `building`, com base no head experimental observado.
2. Cada writer grava chunks com identidade própria `(generation, fence, seq)`.
   Escritas são insert-only. Uma repetição aceita somente bytes idênticos.
3. Antes de cada chunk, o serviço verifica estado, writer, fence e lease. Um
   write atrasado ainda pode vencer uma corrida depois dessa leitura; nesse caso
   ele só cria um chunk órfão daquele fence.
4. A selagem reconstrói e verifica bytes, conteúdo, relações e referências. Um
   CAS de um documento troca `building` por `sealing` e fixa a intenção imutável
   com a lista exata de chunks. Esse CAS é o fencing point: writer antigo não
   consegue substituir a intenção.
5. A intenção é copiada por insert idempotente para
   `poc_editorial_generation_manifests`. A seleção e o leitor consultam essa
   coleção, nunca o registro mutável de build. O estado `sealed` no registro de
   build é apenas informativo; a presença do manifesto íntegro é a fonte da
   geração final.
6. Reinício em `sealing` valida a intenção e repete o insert do manifesto. O
   índice único e o hash tornam a recuperação idempotente. Um conflito diferente
   bloqueia a operação.

Os manifests e chunks são append-only pelo contrato da PoC. Para uma implantação
real, o usuário MongoDB da aplicação deve receber somente `find`/`insert` nessas
duas coleções, sem `update` ou `remove`; builds e heads exigem permissões
separadas. A PoC não cria roles nem comprova essa política no servidor. Um
usuário MongoDB com `readWrite` amplo ainda poderia adulterar esses documentos,
portanto a imutabilidade operacional depende de conceder e testar esses grants.

## Seleção e leitura

`select_active` primeiro valida um manifesto selado e compara a revisão/base que
a geração observou. A mudança de `active_generation_id`, incremento de revisão e
gravação do recibo de idempotência acontecem em um único `update_one` condicional
no head. Isso utiliza a atomicidade de atualização de documento do MongoDB e não
requer transações multidocumento. Até 256 recibos ficam no head; ao atingir o
limite, a PoC falha fechada em vez de descartar idempotência. Produção precisará
de desenho de retenção/particionamento ou de outro formato de recibos.

O leitor resolve o head uma vez e carrega apenas os chunks enumerados no
manifesto daquela geração. Ele valida hashes, sequência, snapshot canônico e
referências. Não há fallback a documentos vivos ou à geração anterior em caso
de corrupção. A projeção omite drafts, gabarito e campos privados conhecidos.
Ela não é contrato de API de produção: antes de ligá-la a leitores reais, cada
tipo de bloco precisa de DTO público allowlist versionado, especialmente para
dados editoriais extensíveis.

## Limites demonstrados

Os testes usam um fake assíncrono determinístico que serializa cada atualização
de documento com lock e permite failpoints/barreiras. Isso verifica os estados,
fencing, conflitos, recuperação, replay e seleção CAS no modelo fake; não prova
wire protocol, índices, durabilidade, concorrência entre servidores reais ou
configuração de permissões do MongoDB. Docker Engine não estava disponível e o
MongoDB local não foi acessado. Uma execução em MongoDB 7 standalone descartável
é pré-requisito antes de afirmar homologação da PoC.

## Migração futura — ordem obrigatória

O mecanismo só pode sair da PoC quando todos os escritores e leitores envolvidos
participarem do mesmo modelo. A migração deve ser aditiva, por trilha em rollout
controlado, mantendo as rotas atuais desabilitadas para ativação até concluir a
matriz abaixo.

1. **Contrato e captura**: definir DTOs versionados, validação de todos os tipos
   de bloco, canonicalização compatível com `ser()`/ObjectId/datas e snapshot de
   tags, taxonomias e block types relevantes. Introduzir um estado editorial
   versionado capturável sem leitura dupla de documentos mutáveis.
2. **CRUD de trilhas, nós, blocos e relações** (`tracks.py`, `nodes.py`,
   `blocks.py`, `relations.py`): passar cada criação, edição, exclusão,
   reordenação, duplicação e alteração hierárquica para uma nova geração
   editável, com CAS no head editorial. Nenhum endpoint legado pode continuar
   gravando as coleções de origem para trilhas habilitadas.
3. **Taxonomias/tags e tipos de bloco** (`taxonomy.py` e rotas): versionar ou
   congelar referências necessárias na geração; a exclusão global de tag não
   pode alterar gerações já seladas.
4. **Importação** (`imports.py`): aplicar o payload inteiramente em geração nova;
   retomar por novo fence e novos chunks, mantendo a geração selecionada atual
   intacta. ` _import_state` permanece bloqueio de seleção até finalização
   explícita.
5. **Restauração** (`versions.py`): converter versão histórica validada em uma
   nova geração. Remover o fluxo delete/reinsert somente após a rota de restore
   operar completamente sobre gerações e preservar IDs de nós/blocos usados por
   progresso, notas, tentativas e submissões.
6. **Seeds e manutenção** (`seed.py`, `manage.py` e scripts): proibir escritas
   diretas em trilhas habilitadas ou adaptá-las ao protocolo; inventariar tarefas
   operacionais e repair scripts antes do rollout.
7. **Publicação**: preparar snapshot, atividades privadas e todas as referências;
   selar manifesto; só então executar CAS do ponteiro real de publicação. Não
   reutilizar o head experimental nem mudar `published_activity_version_id` nesta
   etapa.
8. **Leitores**: migrar listagem, busca, árvore, detalhe de nó/bloco, progresso,
   tentativas, submissões e exportações para resolver uma publicação uma vez e
   filtrar pelo mesmo `generation_id`. Remover fallback para documentos vivos
   após comprovar compatibilidade de conteúdo legado.
9. **Rollout por trilha**: classificar conteúdo legado; trilhas sem revisão
   confiável exigem preparação/revisão administrativa e permanecem não elegíveis
   até validação. Progresso, notas, tentativas, submissões e IDs existentes não
   são reescritos. Manter leitura anterior até uma seleção explícita e plano de
   rollback compatível com os novos dados.

Testes MongoDB 7 standalone devem validar índices únicos, duas instâncias,
recovery após cada failpoint, leituras concorrentes, grants insert-only e limites
do BSON/head. Só depois deles uma fase separada poderá decidir sobre integração
dos escritores ou ativação real.
