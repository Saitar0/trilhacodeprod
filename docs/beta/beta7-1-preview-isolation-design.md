# Beta 7.1 — prévia curricular isolada

## Decisão

A prévia é uma aplicação FastAPI de teste composta explicitamente pelo runner Beta 7.1. Ela não usa `server:app`, não registra o roteador operacional de prévia e não altera o leitor editorial. A composição permite somente handlers selecionados de autenticação e leitura, mais os endpoints de prévia. Não há rota de importação, edição, publicação, promoção ou alteração de grants.

O frontend só registra `/beta7-1-preview` no modo Vite `beta7-1-preview`, com `VITE_BETA7_1_PREVIEW_BATCH_ID` provido pelo harness. O runner verifica essa condição no código servido antes de executar o browser. O servidor operacional continua sem essa rota.

## Prova de isolamento

O harness cria recursos identificados por execução: MongoDB 7 com replica set e WiredTiger, credenciais sintéticas, banco exclusivo, rede Docker interna, contêineres e armazenamento temporário. Não publica portas e não monta volumes. A URI só é entregue ao processo de teste após a inspeção dos IDs, labels, rede, configurações do container e marcador de propriedade. Conexões usam `trust_env=False` no cliente HTTP; não há fallback a `localhost:27017`.

Antes de migrações ou seeds, o gate confirma propriedade e o banco curricular contém apenas o marcador do harness. O conversor e o manifesto são validados antes da primeira gravação. O conteúdo de prévia é guardado no namespace `_beta7_1_preview`, fora das coleções operacionais de leitura; `run_import` é usado apenas para criar a cópia curricular privada e em rascunho no MongoDB descartável, permitindo verificar compatibilidade com os serviços reais.

Evidência da execução final: run `8dad34026a7d4e7ea210301c5754fd08`; MongoDB `7.0.43`, replica set e WiredTiger; rede interna sem portas publicadas; nenhuma publicação; estado curricular `draft/private`; registros de publicação editorial e de atividades iguais a zero. O contexto remove somente recursos próprios identificados. Após a execução, os filtros de container e rede da fase não retornaram recursos.

## Autorização e proteção editorial

Os grants da prévia são sintéticos, escopados pelo lote e pelo usuário: leitura curricular ou revisão do projeto. A autorização também exige usuário autenticado pela rota real de login e sessão válida. Lote inexistente ou fora de escopo é ocultado com 404; aluno autorizado que pede material restrito recebe 403. A resposta pública de projeto é allowlist estrita: somente o brief classificado como público. Marcos sem política de progressão, checklists não classificados e rubrica são omitidos integralmente.

Na mesma execução, o leitor operacional real retorna 404 para a trilha original `draft/private`, enquanto o leitor de prévia retorna a fase ao aluno sintético autorizado. O staging não é promovido e nenhuma publicação é criada. A prova é restrita ao harness: não demonstra IAM operacional nem torna a prévia disponível em inicialização normal.

## Limites

O conteúdo curricular usado continua sendo rascunho aprovado apenas para experimento isolado. Grants, endpoints e namespace da prévia não são um modelo de lançamento. C8–C16, contenção de writers, política editorial operacional, homologação pedagógica e ativação aos Pioneiros continuam pendentes. A rubrica não tem critérios suficientemente aprovados para permitir um resultado `APPROVED`; o fluxo suporta feedback e solicitação de revisão.
