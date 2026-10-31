# Fase 2.1A.12B.5 — revisão do ADR-005: separação público/privado

**Status do ADR original:** Proposed.
**Decisão nesta ficha:** PENDING_APPROVAL.
**Natureza:** recomendação de segurança; nenhum role, coleção ou DTO é alterado nesta fase.

## Problema e evidência

No snapshot `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`, o schema genérico de conteúdo permite campos extras (`backend/schemas/content.py:116-145`) e o serializer genérico remove alguns campos, não é allowlist geral (`backend/serialization.py:8-41`). A publicação de atividade armazena dados privados e públicos no domínio de `activity_publications`; a avaliação do quiz tem projeção específica. O backend usa um `AsyncMongoClient` compartilhado (`backend/database.py:1-8`). A auditoria não verificou grants efetivamente configuradas no banco nem identidade usada por cada processo. Fontes: [auditoria B.2, leitores](./editorial-generations-phase-2-1a-12b2-audit.md), [ADR original](./adr-editorial-generations/ADR-005-public-private-data-separation.md).

O risco é de defesa incompleta: DTO correto reduz saída acidental, mas não limita o que uma credencial de banco comprometida pode ler; um role de coleção não fornece allowlist arbitrária por campo. O relatório não confirma vazamento atual de gabarito em uma rota específica. A vulnerabilidade arquitetural é a possibilidade por schema permissivo, endpoints alternativos e identidade compartilhada desconhecida.

## Recommended Decision — recomendação técnica

Adotar defesa em profundidade:

1. Separar definições privadas de avaliação (gabarito, critérios, rubricas e feedback reservado) dos documentos learner-safe por coleção ou outra fronteira comprovável de privilégios.
2. Usar identidades Mongo distintas: reader público somente leitura em projeções publicáveis; evaluator lê a definição privada da tentativa; editor grava revisões; builder grava candidatos; selector altera somente o controle/head; maintenance/backfill possui identidade temporária e escopo delimitado. Essas são propostas de função, não roles existentes.
3. Projetar cada resposta pública por allowlist explícita e versionada por tipo de bloco e schema. O serializer não copia automaticamente campos desconhecidos. Tipo/schema não suportado resulta em conteúdo indisponível de forma fechada, sem payload parcial ou fallback para documento vivo.
4. Manter autenticação/autorização HTTP independente do principal Mongo. `generation_id` não concede acesso; o servidor valida usuário, sessão, trilha e versão.
5. Restringir logs, métricas e errors: sem conteúdo, respostas, gabaritos, token de sessão, URI, hash privado ou identificadores pessoais. A projeção de cache conserva a mesma allowlist.

Privilégio MongoDB é normalmente aplicado a banco/coleção, não a campos arbitrários. Se o leitor público e o avaliador usam a mesma credencial para a mesma coleção contendo definição privada, uma projeção Python isolada não prova menor privilégio. A arquitetura deve escolher separação física/lógica que permita testar negação de leitura na credencial pública.

## Classificação de dados para a decisão

| Categoria | Política proposta | Evidência/pendência |
|---|---|---|
| Texto, títulos, ordem, hierarquia e mídia destinados ao aluno | Documento público da geração, campos explicitamente permitidos | Classificar campos reais por endpoint e tipo; não copiar documento Mongo bruto |
| Alternativas ou instruções de atividade visíveis antes da resposta | Publicáveis somente após revisão do contrato por tipo | A presença de alternativa não implica que toda metadata do bloco seja pública |
| Resposta correta, gabarito, rubrica e regra de avaliação | Definição privada imutável ligada à tentativa/geração | Quiz já possui versão/public projection limitada; submissions genéricas precisam revisão |
| Feedback reservado, nota/resultado privado e resposta submetida | Dados de tentativa/aluno em armazenamento e API autorizados; fora da geração pública | Classificação depende do modelo de progresso/submission e privacidade |
| IDs internos de writer, fence, lease, receipt, hashes de controle, source revision privada | Somente serviços internos autorizados | Não retornar por endpoint ou erro público |
| Campos extras ou tipo de bloco desconhecido | Rejeitar na projeção pública até adapter/schema aprovado | `extra=allow` existe no snapshot; campos concretos devem ser inventariados |
| Autor, timestamps, metadata de edição/admin | Fora da projeção pública por padrão; só incluir se produto aprovar | Não assumir que os campos atuais têm intenção pública |

## Identidades propostas e mínimo privilégio

| Identidade lógica | Permissões mínimas candidatas | Separação necessária |
|---|---|---|
| Public reader | `find` em head/control mínimo e coleção de geração pública | Sem `find` em drafts, definição de gabarito ou dados do aluno |
| Evaluator | `find` em definição privada versionada e tentativa autorizada; escrita somente no resultado de avaliação conforme contrato | Não administra nem reescreve definição publicada |
| Editorial command | Leitura da revisão-base e inserção de candidate privado; sem escrita direta em geração selada | Sempre associa actor/operation ao controle server-side |
| Builder | Leitura de revisão privada e gravação de manifests/chunks de candidate; sem selecionar head | Payload selado append-only conforme modelo de coleção |
| Selector | Leitura de candidato validado e CAS no documento de controle/receipt permitido | Sem update/delete do conteúdo de chunks |
| Admin preview | Leitura editorial/admin segundo permissões HTTP e projeção distinta do DTO público | Não compartilhar token/DTO público para servir gabarito ou dados de aluno |
| Maintenance/backfill | Operação temporária, auditada, sem pointer público por padrão | Separar de credenciais do serviço web e desabilitar fora da janela aprovada |

O desenho não assume que os papéis atuais atendem a isso. Como a aplicação auditada usa cliente compartilhado, obter isolamento pode exigir múltiplos clientes/connections no mesmo processo ou serviços internos separados; custo, gestão de credenciais e observabilidade devem ser revistos pela operação/security. Não se propõe criar credenciais nesta fase.

## Rotas, cache e coexistência

O inventário da auditoria cobre catálogo, detalhe de trilha, árvore, detalhe do nó/blocos, busca, validate/prerequisites, quizzes, submissions, progresso, notes/reviews, versões/preview admin, `/api/meta` e frontend/React Query. Todos precisam de contrato de audiência. Uma rota legada que serialize documento bruto continua sendo bypass mesmo que o novo reader use DTO estrito.

No cutover público, cada endpoint público resolve e lê a mesma identidade de geração ou usa sessão validada pelo servidor. Cache key inclui audience + geração/sessão; cache público não guarda definição privada. Cache de browser/CDN e erros devem ser revistos; a auditoria não identificou cache HTTP/CDN configurado no snapshot, o que não prova inexistência fora dele. Durante coexistência, a API deve manter a resposta existente ou versionar contrato, mas nunca compor parte do payload de coleção viva e parte da geração.

Migração segura: classificar campos por type/schema; construir representação pública e privada separadamente em ambiente controlado; provar roles de teste; migrar todos os leitores da coorte; bloquear endpoint legado equivalente antes de expor nova geração. Se projeção ou identidade não está pronta, falhar com indisponibilidade explícita, não devolver conteúdo bruto.

## Alternativas e trade-offs

| Alternativa | Vantagem | Risco/custo |
|---|---|---|
| Filtrar no controller | Mudança inicial pequena | Cada rota pode esquecer filtro; principal DB continua podendo ler segredo |
| DTO allowlist somente | Contrato de saída verificável | Não restringe credencial comprometida e pode ser contornado por endpoint alternativo |
| Coleções públicas/privadas separadas | Role pode negar leitura da definição privada | Duplica/projeta dados; builder e retenção precisam manter vínculo versionado |
| Identidades distintas sem separar campos | Credenciais por função | Role de coleção não esconde campos da mesma collection |
| Combinação recomendada | Defesa por storage, credencial, DTO, teste de rota/cache | Mais wiring/roles e governança; alterações de modelo/infra precisam gates próprios |

## Testes e critérios de aceitação

1. Com usuário Mongo público de teste, tentativa de `find` na coleção de gabaritos/drafts é negada; evaluator autorizado lê somente a definição referenciada por uma tentativa.
2. Canários secretos são inseridos em campos extras e não aparecem em catálogo, detail, tree, node, search, activity, preview público, cache, erro ou serialização.
3. Fuzz de campo desconhecido/tipo desconhecido não produz passthrough; projeção falha fechada e sem conteúdo parcial.
4. Quiz A iniciado antes de publicar B é avaliado por identidade privada de A, e a resposta pública nunca contém gabarito.
5. Testes HTTP verificam authz por role/sessão e tentam acessar generation de outra pessoa/trilha; o cliente não escolhe livremente a geração.
6. Testes de log/telemetria provam ausência de respostas, gabaritos, dados pessoais e tokens.
7. Inventário atualizado demonstra que não há endpoint/worker/cache legado que contorne a projeção no escopo ativado.

## Ficha para aprovação

* **Decisão necessária:** aprovar separação pública/privada com storage/identidades distintas e DTO allowlist, ou escolher explicitamente alternativa e aceitar seu risco?
* **Recomendação:** combinação de fronteira de coleção, principals mínimos, allowlists por schema/tipo e negação por padrão.
* **Dependências:** ADR-008 para baseline de implementação; ADR-003 para schemas; ADR-002 para avaliação/sessões; ADR-004 para retenção; ADR-006 para manifest/reader.
* **Responsáveis:** segurança, backend e operações; produto/frontend para campos e payloads.
* **Decisão humana:** PENDING_APPROVAL.
