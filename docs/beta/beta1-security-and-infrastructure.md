# Beta 1 — segurança e infraestrutura

## Evidência e limite

Inspeção estática de C16; nenhum ambiente, Coolify/GHCR, staging, produção, banco, segredo operacional ou arquivo `.env` foi consultado. Configuração versionada não prova o estado implantado. ADR-008 permanece bloqueado e os gates históricos não mudam.

## Identidade e acesso

C16 usa JWT associado a `sid`, consulta sessão ativa, carrega usuário e verifica ativo/desativado, `token_version` e email verificado em `security.py`. `services/sessions.py` cria/verifica/revoga sessão. `constants.py` define `admin`, `editor`, `student` e matriz de permissões Python; `admin` e `editor` recebem escrita editorial global na árvore observada. `permissions.py` verifica permissão global e visibilidade de leitura, não grant de escrita por trilha. Não há prova de equivalência com IAM implantado.

## Risco editorial

C7–C16 demonstram contratos transacionais em isolamento e a prova C16 demonstra que writer direto com credencial DB de escrita contorna CAS/fence/audit do protocolo. Portanto, admin/editor global e operações de import/restore/publish/delete não podem ser considerados seguros por um guard da API sozinho. Antes de permitir edição concorrente de conteúdo publicado, todos os writers relevantes devem cooperar ou ser efetivamente restringidos; uma política de congelamento precisa ter enforcement, não ser só processo verbal.

## Segurança do laboratório

Código no frontend é apenas exibido/copied. Não foi encontrado executor de aluno. Não executar submissions como código. Um futuro laboratório requer workers efêmeros isolados, limites CPU/memória/tempo, filesystem e rede negados por padrão, usuário sem privilégio, limpeza garantida, validação de linguagens/compiladores, quotas e revisão de ameaça; não cabe criar executor improvisado nesta beta.

## Infraestrutura versionada

`compose.yaml` descreve Mongo 7 local com volume, API/frontend e health checks; `compose.qa.yaml` descreve recursos separados e portas configuráveis. Dockerfiles de produção existem. Requirements incluem `pydantic-settings`, PyMongo Async, libs IA e Stripe. CI tem workflows, incluindo testes Mongo e foundation. Nada disso foi executado ou representa homologação.

Pendentes antes de beta: definir host/base, TLS/proxy, origem/CORS, segredo e rotação JWT, SMTP, Mongo auth/roles, backup/restore testados, índices/migrações em plano, health/readiness, logs sem payload sensível, alerta, rate limit, capacidade, suporte e resposta a incidente. Não registrar segredos desta auditoria.

## Dados de aluno e snapshots

Progresso, tentativas e submissões são persistentes no código; a beta precisa isolamento de contas, ACL/retention aprovada, backup/restore e teste de exclusão/restauração que preserve histórico. Se conteúdo publicado mudar, tentativa objetiva aponta a versão publicada original. Os seis testes de snapshot que passaram são unitários/doubles para integridade/limite/ledger, não provam snapshot concorrente, publicação atômica, failover ou preservação total de tentativas.

## Matriz de controle

| Controle | Estado |
|---|---|
| JWT/sessão no código | `IMPLEMENTED_IN_INSPECTED_CODE`; não homologado |
| IAM por trilha | `NOT_FOUND` no código de permissão ativo inspecionado; protótipos são experimentais |
| Atomicidade de writers | `EXPERIMENTAL_ONLY`; bypass direto permanece |
| Backup e recuperação operacionais | `NOT_VERIFIED` |
| HTTPS, secrets, roles e topology implantados | `NOT_VERIFIED` |
| ADR-008/baseline | `BLOCKED` |
| Proteção dos dados de Pioneiros | Decisão operacional e evidência pendentes |
