# Fase 2.1A.12B.4 — gates para implementação e primeira fase proposta

Nenhum gate é considerado aprovado por uma recomendação escrita. Estados atuais: BLOCKED ou PENDING_APPROVAL.

## Matriz de gates

| Gate | Evidência exigida | Estado |
|---|---|---|
| Baseline de implementação | Decisão ADR-008 aprovada com SHA e linha reconciliada | BLOCKED |
| Implantação atual | Digest imutável em execução por ambiente ligado a build/SHA; ou risco explicitamente aceito pelo owner e ambiente isolado escolhido | BLOCKED |
| Estratégia de reconciliação | Inventário de commits/campos e revisão explícita sem merge automático | BLOCKED |
| ADR-001 | Revisão editorial, escritores cobertos, conflitos/retry aprovados | PENDING_APPROVAL |
| Segurança público/privado | ADR-005, grants verificadas por teste e projeções allowlist aprovadas | PENDING_APPROVAL |
| Taxonomias do escopo | Campos/coleções classificados e validados por produto/frontend | PENDING_APPROVAL |
| Sessão/progresso | Política de geração, continuação e tentativas aprovada para cada fluxo afetado | PENDING_APPROVAL |
| Retenção mínima | Referências, obrigações, exclusão e owner de política definidos | PENDING_APPROVAL |
| Contratos internos | Contratos B3 revistos contra baseline selecionado e erros compatíveis aprovados | PENDING_APPROVAL |
| Inventário de writers | CRUD, import, restore, taxonomy, seed, scripts/jobs e migrations reconciliados; dono por via | BLOCKED |
| Inventário de readers | API pública, preview, avaliação, progresso, frontend, cache e jobs reconciliados | BLOCKED |
| Invariantes e testes | Cada invariante ligado a teste unitário/integrado/API/concorrente/segurança | PENDING_APPROVAL |
| Rollback seguro | Procedimento que mantém última geração válida ou interrompe publicação sem retornar ao reader live | PENDING_APPROVAL |
| Observabilidade | Métricas sem conteúdo pessoal/educacional e alertas antes de shadow/piloto | PENDING_APPROVAL |
| Escopo da primeira mudança | Arquivos e comportamento passivo limitados; nenhuma leitura/publicação alterada | PENDING_APPROVAL |
| Autorização para código | Aprovação humana e autorização de implementação para a fase exata | BLOCKED |

## Condições de bloqueio imediato

Não iniciar código que altere runtime se faltar qualquer um destes itens:

1. baseline de código escolhido e relação com os digests implantados documentada;
2. reconciliação com main e staging definida;
3. ADR-001 e ADR-005 aprovados para o escopo;
4. contrato/payload que será preservado e os testes de compatibilidade identificados;
5. todos os writers e readers do escopo reconhecidos;
6. caminho de falha sem fallback aos documentos vivos;
7. autorização independente da mudança.

## Primeira fase executável recomendada

### Fase 2.1A.12B.5 — Reconciliação do baseline e instrumentação passiva

**Objetivo:** fechar a escolha de linha e medir writers/readers reais em ambiente de teste controlado antes de mudar persistência ou resposta pública.

**Dependências:** evidência de implantação (ou escolha formal de ambiente isolado), decisão ADR-008, owner de produto/operação e política de privacidade para logs.

**Arquivos candidatos após baseline aprovado:** serviços e rotas editoriais identificados na auditoria B2, em particular backend/services/tracks.py, nodes.py, blocks.py, relations.py, imports.py, versions.py, taxonomy.py, backend/manage.py e pontos de API correspondentes. Os caminhos exatos devem ser refeitos contra o commit escolhido; os nomes acima referem-se ao snapshot e5.

**Comportamento permitido:** observabilidade passiva de operação, rota lógica, track ID pseudonimizado, revisão disponível se já existir, resultado e correlation ID; contadores de chamadas por classe de writer/reader; nenhuma gravação editorial extra. Não registrar payload, gabarito, URI, token, dado de aluno ou conteúdo.

**Comportamento proibido:** alterar payload HTTP, autorização, ordem de escrita, estado editorial, transação, seleção de versão, cache, feature flag pública ou comportamento de falha. Não criar índice, coleção, migration ou backfill.

**Flags:** se a instrumentação precisar de controle, propor apenas EDITORIAL_WRITE_AUDIT_ENABLED=false como emissão diagnóstica; não é autorização para ativar agora. A ausência do flag não pode mudar a lógica de negócio.

**Testes:** testes unitários de evento/log sanitizado; teste que prova payload sensível não aparece; testes de contrato existentes; comparação funcional do endpoint antes/depois; validação em ambiente descartável. Sem banco real.

**Gate:** nenhum runtime até baseline escolhido; antes de avançar para integração de writers, demonstrar cobertura das vias CRUD/import/restore/taxonomy/scripts e ausência de conteúdo sensível na telemetria.

**Reversão:** desabilitar/remover somente observabilidade; nenhum dado editorial precisa ser revertido; manter logs já coletados segundo política aprovada.

**Risco:** instrumentação pode omitir via indireta ou gerar identificadores pessoais. Mitigar com allowlist de campos, revisão de segurança e teste de sanitização.

Esta é uma proposta futura, não autorização para implementação nesta fase.

## Roadmap pequeno e condicional

| Fase proposta | Objetivo | Gate principal |
|---|---|---|
| 2.1A.12B.5 | Selecionar baseline e instrumentação passiva | ADR-008 e privacidade |
| 2.1A.12B.6 | Contrato de revisão/fencing em serviço isolado e testes | ADR-001; sem trocar writer público até todos os caminhos mapeados |
| 2.1A.12B.7 | Adaptar writers por classe, começando por CRUD controlado | Writer inventory zero bypass para escopo |
| 2.1A.12B.8 | Persistência privada, índices aditivos e builder sombra | ADR-003/005; grants e restore testados; sombra sem efeito público |
| 2.1A.12B.9 | Backfill idempotente e relatório de comparação | elegibilidade/retention; nunca selecionar head |
| 2.1A.12B.10 | Leitor alternativo versionado por escopo controlado | ADR-002/005; contract/E2E e rollback sem live fallback |
| 2.1A.12B.11 | Seleção atômica e restore como nova geração | ADR-001/006; CAS, fencing, replay e failpoints |
| 2.1A.12B.12 | Rollout e desativação de legados | ADR-007; zero bypass e janela de métricas aprovada |

Cada fase exige sua própria autorização, revisão de diff, evidências e reversão. A ordem pode mudar apenas após decisão humana e dependências explicitadas.
