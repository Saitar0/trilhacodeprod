# Fase 2.1A.12B.3 — invariantes de segurança e consistência propostos

**Status:** proposta para aprovação; nenhum invariante abaixo está implementado como garantia da aplicação.
**Baseline de evidência:** e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636.
**Referência experimental:** PoC commit 8a087fd5baa9e2eaa98bc1d2ed52b4a60f8c7036, run 40686021030; somente comportamento da PoC foi homologado.

| ID | Invariante proposto | ADR | Componente responsável | Teste necessário | Gate de ativação | Severidade se violado |
|---|---|---|---|---|---|---|
| INV-01 | Revisão editorial é monotônica e nunca inferida por contagem de documentos | 001 | EditorialRevisionContract | Atualização de campo com cardinalidade constante | Contrato de revisão aprovado | Crítica |
| INV-02 | Toda escrita de conteúdo que afeta geração passa pelo mesmo revision/fence; writer não inventariado bloqueia cutover | 001,007 | Todos CRUD, import, restore, taxonomy semântica, seed/manutenção | Scanner + instrumentação de bypass; concorrência por writer | 100% de writers no escopo mapeados e cobertos | Crítica |
| INV-03 | Candidate derivado de uma revisão completa e identificada; não de leituras vivas independentes | 001,006 | Revision store e builder | Editar documentos distintos durante build; origem deve ser única revisão ou rejeitar | ADR-001 aprovado e revisão imutável disponível | Crítica |
| INV-04 | Comando sobre revisão-base obsoleta não escreve nem rebaseia silenciosamente | 001 | Command service | Dois comandos concorrentes; perdedor retorna conflito sem efeito | Política de conflito/API aprovada | Alta |
| INV-05 | Fence obsoleto não grava, sela, confirma nem seleciona conteúdo | 001,006 | Writer/builder/selector | Takeover + writer atrasado em cada transição | Todos os writers validam fence | Crítica |
| INV-06 | operation_id reutilizada com fingerprint diferente conflita | 001,006 | Receipt/command store | Retry idêntico versus payload alterado | Idempotency schema e erro aprovados | Alta |
| INV-07 | Geração sealed e seus chunks/manifest são imutáveis; correção cria identidade nova | 006 | Builder/storage roles | Tentativa de update/replace/delete por writer append-only | Grants reais comprovadas | Crítica |
| INV-08 | Manifesto, sequência, tamanho, hash e referências correspondem aos chunks existentes | 006 | Integrity validator | Missing/duplicate/corrupt/reordered chunk | Validador integrado passa em Mongo real | Crítica |
| INV-09 | Geração parcial ou tipo/schema não suportado nunca é selecionável | 003,006 | Builder/selector | Failpoints e bloco desconhecido | Gate de schema e validação aprovado | Crítica |
| INV-10 | Head ativo referencia somente geração sealed, íntegra, autorizada e derivada de revisão válida | 001,006 | PublicationContract | CAS contra revisão/head divergente | CAS standalone comprovado | Crítica |
| INV-11 | Seleção do head é uma única escrita condicional de documento; sem garantia implícita de transação multidocumento | 006 | Selector | Integração standalone, assert nenhuma transaction command | Topologia aprovada | Crítica |
| INV-12 | Resultado de seleção repetido por mesma operation_id devolve receipt original | 001,006 | Receipt store | Perda simulada de resposta após commit | Idempotência e índice unique verificados | Alta |
| INV-13 | Leitor resolve geração uma vez por operação/sessão e não mistura IDs | 002,006 | Public reader/session | Swap A/B entre tree, node e chunks | Toda rota/caches cobertos | Crítica |
| INV-14 | Erro de integridade não faz fallback para documentos vivos nem entrega payload parcial | 005,006 | Reader/API | Corrupção de head/manifest/chunk | Runbook e comportamento de indisponibilidade aprovados | Crítica |
| INV-15 | DTO público segue allowlist; campo desconhecido não é copiado | 005 | Projector/API/cache | Fuzz de campos extras e canários em todas rotas | Aprovação de segurança dos DTOs | Crítica |
| INV-16 | Identidade pública não tem leitura de coleção/partição de gabaritos/rubricas | 005 | Mongo roles/storage | Teste de grants reais com usuário público | Prova de menor privilégio em Mongo real | Crítica |
| INV-17 | Tentativa fixa a geração e definição privada avaliadas; head corrente não muda o gabarito da tentativa | 002,005 | ActivityEvaluationContract | Iniciar em A, publicar B, submeter resposta de A | Política de tentativa/histórico aprovada | Crítica |
| INV-18 | Progresso/submission/histórico não é copiado para conteúdo editorial e não perde a referência pedagógica definida | 002,004 | Progress/submission services | Publicação, restore, delete/tombstone, retomada | Semântica de produto e retenção aprovada | Alta |
| INV-19 | Conteúdo, taxonomia, schema ou renderer semanticamente relevante é versionado ou congelado | 003 | Builder/renderer/evaluator | Alterar metadado global depois de A | Matriz campo/owner aprovada | Alta |
| INV-20 | Backfill nunca muda active_generation_id e é idempotente pela identidade de origem | 004,007 | Backfill tool | Repetição, interrupção, resume e assert pointer imutável | Autorização separada de operação de dados | Crítica |
| INV-21 | Shadow build/comparison não altera resposta pública nem executa efeitos do writer legado | 007 | Builder/comparator | Comparação sem writes públicos; auditoria de side effects | Métrica de divergência e owner aprovados | Alta |
| INV-22 | Flags começam desabilitadas e são independentes; combinação insegura falha fechada | 007 | Configuração/rollout | Matriz de combinação de flags | Change approval e owner registrados | Crítica |
| INV-23 | Cutover bloqueia escritores legados; nenhuma flag permite payload misto live/generation | 001,006,007 | API, jobs, scripts, reader | Writer coverage e concorrência end-to-end | Zero bypass no escopo e audiência | Crítica |
| INV-24 | GC não remove head, candidate em operação ou geração referenciada por sessão/tentativa/histórico/receipt | 004 | Lifecycle/GC | Referência concorrente durante grace e recheck | Política de retenção/legal e referência completa | Crítica |
| INV-25 | Retirada urgente revoga acesso sem mudar silenciosamente a identidade ou o resultado histórico | 002,004,006 | Revocation/session/reader | Sessão ativa em geração revogada | Política de incidentes/UX aprovada | Alta |
| INV-26 | Rollback pós-cutover não habilita leitura legacy mutável automaticamente | 006,007 | Release/feature control | Drill de código flag off e reader indisponível | Runbook de parada aprovado | Crítica |
| INV-27 | Logs/metrics não contêm conteúdo, respostas, gabaritos, dados pessoais ou tokens | 005,007 | Observabilidade | Teste de canário/regex e revisão de log | Privacy/security review | Alta |
| INV-28 | IDs estáveis preservados ou migração explícita liga progresso, attempts e referências históricas | 002,004,008 | Migration/adapters | Contract e orphan audit | Baseline e regra de compatibilidade aprovados | Alta |

## Uso dos invariantes

Cada fase futura deve declarar quais IDs implementa, quais testes os comprovam e qual owner aceita o risco residual. A existência de teste fake ou aprovação da PoC não demonstra invariantes no backend real. INV-02, INV-10, INV-13, INV-15, INV-16 e INV-26 são gates bloqueantes para seleção pública.

## Fontes e confiança

Os riscos atuais vêm do audit B.2 seções 2-5, código e5bf…: services/tracks.py:152-227; backend/services/versions.py:142-159,245-332; backend/services/immutable_publications.py:487-510; backend/services/nodes.py:27-149,234-256; backend/schemas/content.py:116-145; backend/database.py:1-8; frontend/src/hooks/useData.ts:19-40. Confiança alta para a estrutura do snapshot; deployment e grants reais não foram verificados. Todas as linhas desta tabela são recomendações futuras.
