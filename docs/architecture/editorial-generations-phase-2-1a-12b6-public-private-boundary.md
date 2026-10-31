# Fase 2.1A.12B.6 — Fronteira proposta entre conteúdo learner-safe e dados privados

**Status:** PROPOSED, sujeito a revisão de segurança e produto.
**Baseline estático:** `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`. Papéis MongoDB e configuração de produção não foram comprovados.

## 1. Regra central

“Visível ao aluno autenticado” não significa “público anônimo”, e “está numa geração publicada” não significa “pode ser serializado”. A resposta deve ser construída para um contexto autorizado por allowlist explícita. Gabaritos, rubricas, campos de controle e rascunhos nunca podem depender apenas de filtragem por controller ou de remover nomes conhecidos.

## 2. Evidência atual

| Evidência observada no código | Consequência | Confiança |
|---|---|---|
| `backend/schemas/content.py:116-145`: modelo-base de conteúdo aceita extras (`extra="allow"`). | Campos futuros ou vindos do armazenamento podem entrar em DTO amplo sem rejeição. | Alta |
| `backend/serialization.py:24-41`: serialização genérica remove campos privados conhecidos, não aplica allowlist de conteúdo por endpoint. | Campo privado novo não incluído no denylist pode vazar em rota que use serializer genérico. | Alta |
| `backend/database.py:3-8`: cliente/banco compartilhado é importado por serviços. | Não há evidência de principals de leitura pública e avaliação separados. | Alta no código; papéis efetivos desconhecidos |
| `backend/services/activity_publications.py:155-169`: `public_activity` seleciona campos de quiz explicitamente e valida definição. | Salvaguarda positiva localizada, não prova cobertura de todos os readers/endpoints/cache. | Alta |
| `backend/services/nodes.py:85-149`: leitura agrega node/block/relation vivos com publicação de atividade. | Projeção de quiz limitada não protege campos extras de outros blocos nem coerência geral da resposta. | Alta |
| `backend/services/activities.py:72-107,128-190,347-...`: avaliação busca a definição vinculada à versão persistida na tentativa. | Pin de quiz por tentativa existe no snapshot; não comprova identidade DB segregada nem pin de sessão completa. | Alta |

Permissões/roles MongoDB, grants por coleção, endpoint coverage efetivo e caches de produção: `BLOCKED/UNKNOWN`; não foram consultados.

## 3. Classificação proposta de dados

“Publicável” significa elegível para uma resposta de aluno depois de autorização e seleção da geração; não significa leitura anônima. Classificação é conceito de domínio; revisar cada tipo de bloco e campo com produto/segurança.

| Categoria observada/conceitual | Classificação proposta | Quem pode ler | Quem pode escrever | Serialização e falha |
|---|---|---|---|---|
| Título, descrição, hierarquia, ordem, texto e mídia didática validados | Learner-safe de geração publicada | Reader de aluno autorizado; catálogo público somente campos aprovados | Comandos editoriais e builder | DTO allowlist; campo desconhecido ou schema sem renderer suportado rejeita geração/resposta |
| Opções/alternativas visíveis antes da resposta | Learner-safe apenas conforme tipo de atividade | Reader de atividade autorizado | Comando editorial | Allowlist por tipo/version; nunca inferir que todo `content` é seguro |
| Resposta correta, gabarito, rubrica, critérios, chave de avaliação e feedback reservado | Privado imutável | Serviço avaliador; staff explicitamente autorizado | Comandos editoriais/builder privilegiado | Coleção/partição privada; evaluator DTO mínimo; negado por padrão |
| Rascunhos, revisão em construção, conteúdo rejeitado, chunks candidate | Editorial privado | Editor/builder/reviewer autorizado | Serviço editorial/builder | Não acessível ao principal do reader de alunos; não serializar em erro |
| Metadata administrativa, autoria interna, notas de edição, import job, lease, fencing, operation fingerprints | Operacional privado | Serviço editorial/auditoria | Serviço correspondente | Nunca no DTO público; logs por allowlist e sem payload sensível |
| IDs estáveis de trilha/nó/bloco, `generation_id`, `schema_version` | Identificador interno/contextual | API pode expor somente identificador necessário ao contrato; sessão é validada pelo servidor | Serviços | Não é segredo nem autorização; cliente não escolhe geração arbitrariamente |
| Tags, taxonomia, tipo de bloco e capabilities | Semântica versionada ou metadata administrativa conforme campo | Reader/catalog apenas campos aprovados | Owner editorial/taxonomia | Fixar versão se afetar navegação/render/avaliação; tipo desconhecido falha fechado |
| Tentativas, submissões, progresso, notas e identificador de aluno | Dado pessoal/educacional fora do snapshot editorial | O próprio aluno e serviços autorizados; staff segundo política | Serviços de aprendizagem | Autorização por usuário/curso; não copiar para geração; acesso e logs mínimos |
| Auditoria de seleção, digest, receipts e referência de restore | Interno de segurança/auditoria | Operador/auditor autorizado | Serviços de controle | Sem respostas privadas nos logs; retenção pendente de ADR-004 |

## 4. Arquitetura de defesa em profundidade

### Recomendação preferencial

1. Guardar rascunhos e candidates em namespace privado sem leitura pelo principal de aluno.
2. Guardar definições privadas de avaliação numa coleção/partição privada imutável, com reader exclusivo do serviço avaliador.
3. Separar payload learner-safe publicado da área de draft/candidate para que permissão por coleção não exponha candidates não selecionados. Se usar uma coleção comum, MongoDB collection-level grants não filtram por `generation_id`; a proteção dependeria totalmente do serviço, lacuna que exige aprovação explícita.
4. Criar principals de menor privilégio por serviço (editorial/builder, public reader, evaluator, manutenção); verificar grants reais em fase de implementação. Credenciais atuais não foram auditadas.
5. Aplicar DTO versionado e allowlist no boundary de resposta; proibir passthrough de Mongo document, `extra=allow` e serializers de denylist nas respostas cobertas.
6. Validar projeção na selagem e novamente na leitura; unknown fields/capabilities não são retornados parcialmente.
7. Auditar todos os caminhos: catálogo, árvore, detalhe, bloco, atividade, preview, busca, cache, progresso, avaliação, export e erro. Cache key inclui identidade da geração e classe de audiência; invalidação não deve servir geração cross-user ou privada.

### Alternativas

| Alternativa | Benefício | Limitação |
|---|---|---|
| Filtrar no controller | Pouca mudança inicial | Fácil omitir rota e campo; não protege DB/query/cache; fail-open por código |
| DTO allowlist sozinho | Boundary verificável e compatível | Serviço ainda pode ler gabarito; falha de rota alternativa permanece |
| Coleções separadas no mesmo banco | Menor custo operacional; grants por coleção possíveis | Admin principal pode acessar ambas; learner-safe candidates precisam namespace diferente |
| Bancos separados | Fronteira e backup/restore mais fortes | Operação, referências e consistência mais complexas; não elimina erro de API |
| Principals distintos | Menor privilégio técnico | Não filtra documentos por linha; processo público não deve receber coleção privada |
| Serviço/identidade + coleções separadas + DTO allowlist | Defesa em profundidade | Mudança de arquitetura, deploy, roles e testes; precisa plano de migração |

Recomendação: combinação de isolamento lógico/coleções e principals distintos, DTO allowlist e testes negativos. A decisão entre bancos e coleções separados depende do threat model e operação, não está resolvida pela PoC.

## 5. Contratos conceituais

### `ProjectLearnerContent(generation_id, resource_id, audience_context)`

- Valida usuário/sessão e que generation é a sessão fixada ou ativa escolhida pelo servidor; não aceita ID como autorização.
- Consulta somente objetos learner-safe publicados daquele generation e versão de schema/taxonomia.
- Serializa campos permitidos por versão de contrato; nenhum documento Mongo é retornado diretamente.
- Campo obrigatório ausente, chunk inválido, schema desconhecido ou autorização ambígua resulta indisponibilidade segura, sem fallback live.

### `LoadPrivateEvaluation(activity_definition_id, attempt_id, actor)`

- Serviço avaliador verifica que a tentativa pertence ao ator e que a definição corresponde ao pin imutável nela persistido.
- Reader de aluno não possui grant sobre definição privada; evaluator retorna só o resultado necessário.
- Versão ausente/corrompida ou permissão negada não usa gabarito atual como substituto; tentativa fica pendente de reconciliação/erro seguro.

### Erros públicos

Erro público informa indisponibilidade genérica e correlation ID não sensível; nunca inclui documento, gabarito, fingerprint, lease, query, URI ou stack. Logs internos têm campos estruturados permitidos e redaction.

## 6. Cache e compatibilidade

- Cache de conteúdo inclui `generation_id`, versão do DTO/schema e audience (anônimo, aluno autenticado, staff), além dos parâmetros de projeção. Não reutilizar resposta privada em cache público.
- Sessões antigas podem fixar geração; cache não pode substituir geração fixada pelo head corrente.
- Introduzir projeção nova atrás de adapter e contrato aditivo; resposta incompatível exige versionamento explícito. Não aceitar campo desconhecido como resposta automática.
- Retirada urgente invalida/nega acesso segundo política aprovada; não servir conteúdo privado por fallback nem silently retarget para nova geração.

## 7. Critérios de teste e aceitação

1. Fixture com todos os campos sensíveis conhecidos e um campo privado inesperado; resposta pública contém apenas allowlist.
2. Gabarito/rubrica ausentes do catálogo, árvore, preview não autorizado, busca, blocos, logs e erro.
3. Principal learner falha ao ler coleção privada; evaluator autorizado lê somente tentativa/definição correspondente.
4. Tentativa A após geração B usa definição A; ID alterado ou de outro usuário é negado.
5. Cache sob A não retorna payload B ou staff; cache key prova audience e generation.
6. Unknown block/schema, chunk ausente/corrupto ou grant negado falha fechado, sem leitura legada.
7. Integração com grants reais em ambiente MongoDB descartável semelhante à topologia alvo; PoC anterior não comprova roles do app.

## 8. Decisões humanas

- Produto/segurança classificam campo a campo o conteúdo exibível ao aluno e os níveis de anonimato/autenticação.
- Segurança decide se mesmos DB com collections/grants bastam ou se separar bancos/principals/processos.
- Avaliação de privacidade define acesso a tentativas/notas, logs e histórico.
- Engenharia confirma formato/compatibilidade de payloads existentes e inventário de endpoints e caches para baseline aprovado (ADR-008 segue bloqueado).

## 9. Referências

- `backend/schemas/content.py:116-145`; `backend/serialization.py:24-41`.
- `backend/database.py:3-8`; roles efetivas: não comprovadas.
- `backend/services/activity_publications.py:155-169`.
- `backend/services/activities.py:44-107,128-190,347` (`submit_attempt`).
- `backend/services/nodes.py:85-149`.
- [`ADR-005 original`](./adr-editorial-generations/ADR-005-public-private-data-separation.md), [`contrato de geração`](./editorial-generations-phase-2-1a-12b6-generation-contract.md).
