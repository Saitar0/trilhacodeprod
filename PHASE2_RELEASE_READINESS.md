# Trilha Code — Fase 2R: prontidão para release

**Data:** 16/10/2026  
**Estado:** preparação documental e preflight somente leitura implementados. Nenhum banco foi acessado; nenhuma migração, criação de índice, pipeline remoto ou publicação foi executada.

## 1. Evidências confirmadas e pendências

### Confirmado por inspeção nesta preparação

- `backend/manage.py` oferece comandos separados: `preflight-indexes` (novo, somente leitura), `migrate` (migrações de dados), `ensure-indexes` (criação/verificação idempotente via `create_index`) e outros comandos administrativos. Startup não chama `ensure_indexes`.
- `migrate` não cria índices. O startup da API verifica schema mínimo versão 2 e recusa servir com schema antigo.
- As migrações obrigatórias são `0001_legacy_snapshots` (move snapshots embutidos para chunks comprimidos) e `0002_block_submission_capabilities` (atualiza tipos de bloco existentes e grava marcador auxiliar). `migrate` usa lock/lease e registra versões.
- `backend/indexes.py` contém 23 especificações. `preflight-indexes` inspeciona existência/opções e procura duplicatas para todas as chaves únicas, aplicando filtro quando o índice é parcial. `ensure-indexes` usa as mesmas especificações. Preflight não escreve e não garante que estado não mude depois da checagem.
- A API usa imagem Python 3.11 slim, instala `backend/requirements.prod.txt`, que inclui `pymongo==4.18.2`; não há Motor nos manifests/código backend inspecionados. Healthcheck da imagem chama `/health`.
- Frontend usa Node 20 Alpine para build, `npm ci`, Vite, TypeScript e Tailwind 4 (`tailwindcss` e `@tailwindcss/postcss`); runtime Nginx Alpine serve `dist` na porta 8080 e tem healthcheck HTTP em `/`.
- O workflow tem jobs independentes `backend` e `frontend`; ambos os jobs de deploy dependem dos dois. Backend usa Python 3.11/MongoDB 7; frontend usa Node 20 e `npm ci`. Push e PR executam somente validação. Publicação agora requer `workflow_dispatch` manual, input `staging`/`production`, branch correspondente e jobs verdes; o padrão é `none`. Jobs estão associados aos GitHub Environments correspondentes.
- Foi adicionado `workflow_dispatch` com alvo `none` como padrão para CI completo sem deploy e controle manual separado de publicação. A execução manual não foi disparada.

### Evidências anteriores fornecidas, não repetidas nesta etapa

- 63 testes backend passaram em execução externa com MongoDB de teste, conforme contexto da Fase 2. O relatório final registra divergência com artefatos antigos que diziam que a suíte não foi executada; anexar log/URL de CI da execução que passou ao release candidato.
- Frontend teve anteriormente `npm ci`, typecheck, ESLint, Vitest, build e `npm audit` aprovados, mas o `npm ci` limpo desta sessão estava inconclusivo segundo `PHASE2_FINAL_REVIEW.md`.
- Ruff, compilação Python e checagens anteriores aprovadas estão registradas em `PHASE2_FINAL_REVIEW.md`; não substituem CI verde no commit que será promovido.

### Pendente

- CI atual verde no commit candidato (incluindo `pip-audit`, `npm audit`, builds e testes).
- Backup e restore testado; preflight, migrações e índices aplicados e verificados em staging com cópia representativa dos dados.
- Medidas de duração/recursos para preflight e criação dos índices no volume de staging.
- Inspeção visual manual de todas as áreas listadas na seção 4.
- Proteções/aprovadores configurados nos GitHub Environments `staging` e `production`; `environment:` no workflow não configura aprovação por si só. Auto-deploy por push no Coolify desativado.
- Revisão/registro operacional dos secrets, identidade do banco/ambiente, espaço disponível e métricas de latência.

## 2. Checklist operacional

Use a sequência completa da seção 7 de [DEPLOY.md](DEPLOY.md). Resumo dos gates:

- [ ] Commit e artefatos/CI identificados; backend e frontend verdes.
- [ ] Branch e aprovação de release registradas; janela, operador e rollback definidos.
- [ ] Backup recente concluído e recuperável; restore de teste válido.
- [ ] URI, credenciais, host/cluster e `DB_NAME` confirmados por dupla checagem para o ambiente alvo.
- [ ] Preflight antes da migração sem conflito/duplicata; segundo preflight limpo após migração.
- [ ] Migrações versão 2 concluídas; logs e lock verificados.
- [ ] `ensure-indexes` completou; preflight final reporta todos os índices compatíveis.
- [ ] Métricas de disco, CPU, memória e latência aceitáveis; janela ainda válida.
- [ ] API `/health` e `/ready` saudáveis; smoke test em staging passou.
- [ ] Inspeção visual em desktop e mobile aprovada com evidência anexada.
- [ ] Aprovação manual de production e plano de comunicação disponíveis.

## 3. Estratégia de CI sem deploy

Use PR destinado a `main`/`staging`, push a essas branches ou `workflow_dispatch` na branch/commit candidato com alvo `none`. Todos executam jobs backend e frontend sem deploy. Publicação exige evento manual, input específico de alvo e branch correspondente. Nenhum dos jobs de validação exige secrets Coolify.

O workflow mantém validação e publicação em jobs separados; deploy depende dos dois. A separação em outro arquivo não é necessária para executar CI sem deploy, pois push/PR são somente validatórios e o dispatch usa `none` por padrão. Habilite proteção de branch para exigir ambos os checks e bloquear bypass; configure aprovação obrigatória nos GitHub Environments `staging`/`production`; desative auto-deploy por push no Coolify para que ele não contorne o gate. Preserve os secrets existentes; nunca os exponha aos jobs de validação.

## 4. Homologação visual manual

Não há aprovação visual nesta preparação. Faça a inspeção no staging com dados de teste, sem credenciais de production. Percorra fluxos completos e registre capturas de tela, navegador/versão, viewport, commit e resultado.

### Fluxos e áreas

- [ ] Login, mensagens de erro, sessão, logout e registro.
- [ ] Perfil: leitura, edição, validações e estados vazios/erro.
- [ ] Dashboard do aluno: carregamento, cards, métricas, estados sem dados.
- [ ] Lista de trilhas, busca/filtros e estados vazios.
- [ ] Visualizador de conteúdo: navegação entre nós, blocos, markdown, código, vídeo e conteúdo longo.
- [ ] Editor de trilhas: criar/editar, ordenação, publicação/rascunho e confirmação de saída.
- [ ] Editor de blocos: tipos diferentes, campos obrigatórios, validação, preview, adicionar/remover/reordenar.
- [ ] Administração: tabelas, paginação, busca/filtros, ações, formulários, validação e feedback.
- [ ] Submissões: enviar, estados de carregamento/erro/sucesso, tentativas e reenvio.
- [ ] Avaliação: lista pendente, detalhes, feedback, nota/resultado e confirmação.
- [ ] Modais, dropdowns, menus, navegação, botões e links em todos os fluxos.

### Viewports e estados visuais

- [ ] Desktop (largura de referência 1440 px) e tablet/laptop (1024 px).
- [ ] Mobile (390 px e 360 px), orientação retrato; sem scroll horizontal não intencional.
- [ ] Cores, contraste, tipografia, espaçamentos, alinhamento e consistência dos componentes.
- [ ] Modal/overlay, scroll interno, fechamento por botão/tecla, clique externo quando previsto.
- [ ] Menus abrem/fecham e não ficam cortados ou atrás de overlays.
- [ ] Ícones alinhados, com tamanho consistente e sem glifos ausentes.
- [ ] Hover e focus visíveis; navegação por teclado e foco dentro/fora de modal.
- [ ] Loading, sucesso, vazio, erro de validação e erro de rede.
- [ ] Sem erros de console, recursos 404, falhas de fonte/imagem, CORS ou cookies.
- [ ] Navegadores suportados pelo público validados contra Tailwind 4.

**Aprovação visual:** preencher apenas após execução real em navegador e anexar evidências. Build bem-sucedido não substitui inspeção visual.

## 5. Política de índices e duplicidades

- Fonte da verdade: especificações centralizadas em `backend/indexes.py`.
- `python -m backend.manage preflight-indexes`: leitura de especificações existentes e agregações para duplicatas de chaves únicas. Saídas `OK`, `AUSENTE`, `CONFLITO` ou `DUPLICATAS`. Código de saída falha se houver conflito/duplicata ou erro inesperado. `AUSENTE` isolado é esperado antes da criação.
- `python -m backend.manage migrate`: escreve dados/schema; não cria índices.
- `python -m backend.manage ensure-indexes`: cria os índices ausentes e aceita índices já compatíveis; não corrige opções conflitantes nem remove índices.
- Não adicionar criação automática de índices ao startup. Aplicação e timing requerem janela, capacidade do banco, backup e aprovação operacional.
- Duplicatas devem ser analisadas por responsável de dados/produto. Definir registro canônico, impacto referencial e correção em mudança separada, com backup e validação. Não excluir/mesclar automaticamente no deploy.
- Segurar escritas concorrentes relevantes do início do preflight até conclusão do `ensure-indexes`, para reduzir risco de corrida.

## 6. Riscos e rollback

| Risco | Efeito | Controle |
| --- | --- | --- |
| Migração parcial/falha | Dados parcialmente atualizados ou startup recusado se schema < 2 | Backup, janela, logs; não subir nova API; investigar estado e reexecutar apenas após confirmar idempotência/estado da migração |
| Duplicatas/conflicto de índice | Índice único não cria; `ensure-indexes` encerra | Preflight pré e pós migração; correção de dados aprovada fora do deploy |
| Preflight e build de índice longos | Carga em CPU/memória/I/O, latência e uso de disco | Medir em staging, janela, margem de disco, monitoramento; abortar se limite definido for cruzado |
| Criação parcial dos 23 índices | Índices anteriores ficam instalados se um posterior falhar | Registrar quais foram criados; corrigir causa; preflight e rerun idempotente; sem remoção automática |
| Deploy quebra apesar de CI | API/UI indisponível ou fluxo regressivo | Staging, smoke tests, `/health`, `/ready`, logs e métricas; rollback da aplicação |
| Rollback de código incompatível com schema | Versão anterior não entende schema/dados novos | Migrações compatíveis para trás; validar versão anterior em staging; preferir rollback só do app |
| Restore de backup | Perda de gravações posteriores ao snapshot | Aprovação do dono do banco, janela e plano explícito; restore apenas como recuperação de dados |

Rollback preferencial: reimplantar commit/imagem anterior e confirmar health, readiness, login, leitura e logs. As migrações desta fase não possuem downgrade documentado; não presumir reversibilidade. Não restaurar backup para resolver problema de app sem avaliar perda de gravações posteriores.

## 7. Plano de staging

1. Preparar banco staging isolado e dados sintéticos ou cópia anonimizada, com volume representativo; nunca compartilhar banco, credenciais ou `DB_NAME` com production.
2. Guardar backup/snapshot inicial e confirmar restore de teste.
3. Executar CI manual ou em PR no commit candidato e guardar URL/log de todos os jobs.
4. Medir preflight antes de migração; registrar início/fim, CPU, memória, I/O e latência. Resolver qualquer duplicata/conflito em preparação separada.
5. Aplicar migrate; confirmar versão 2; executar segundo preflight.
6. Executar ensure-indexes; registrar duração, log, consumo de espaço e qualquer índice criado. Executar preflight final e comparar todos os 23 índices.
7. Deploy de staging pelo processo autorizado; validar `/health`, `/ready`, logs, autenticação, smoke tests e checklist visual completo.
8. Observar por período acordado métricas e erros. Só então preparar decisão de production com registro de evidências e janela.

## 8. Critérios objetivos de aprovação para production

Production só recebe aprovação quando todos os itens abaixo forem verdadeiros:

1. CI do commit exato verde nos jobs backend e frontend, incluindo testes, Ruff, compilação, builds e auditorias de dependências; evidências históricas resolvidas por log verificável.
2. Nenhum bug bloqueador/alto aberto; checklist visual completo aprovado em desktop/mobile com evidências anexadas.
3. Staging executou migrações e os 23 índices no banco representativo; preflight final só contém `OK`; tempos e margem de recursos estão dentro dos limites definidos pelo responsável operacional.
4. Backup pré-release verificável e restore de teste recente; espaço livre adequado para build de índices e crescimento planejado.
5. `DB_NAME`, host, credencial e branch production revisados por duas pessoas; branch protegida, aprovação manual de environment ativa e secrets de produção restritos. O dispatch manual com alvo production só ocorre depois da sequência operacional de banco.
6. Janela, operador, plano de comunicação e decisão de abortar definidos; rollback de aplicação ensaiado e compatibilidade do schema anterior confirmada.
7. Em staging, `/health` e `/ready` saudáveis, schema 2, autenticação e fluxos críticos validados, sem erros novos relevantes nos logs/monitoramento.

## 9. Limite de autorização desta preparação

Pode ser validado localmente: leitura/compilação estática, CI em PR/workflow_dispatch sem deploy, revisão dos comandos e testes em Mongo descartável criado especificamente para isso. Build Docker só se daemon local estiver disponível e build não compartilhar/alterar estado de containers existentes.

Exige autorização operacional e execução pelo responsável: conectar a qualquer banco existente, obter/usar credenciais, backup/restore real, preflight em staging/production, migrações, `ensure-indexes`, correção de dados, criação/configuração de ambientes protegidos ou secrets, disparo de push/workflow de deploy e qualquer publicação. Nenhuma dessas ações foi feita nesta preparação.
