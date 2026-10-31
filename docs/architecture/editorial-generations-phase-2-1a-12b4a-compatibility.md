# Fase 2.1A.12B.4A — compatibilidade entre runtime observado e Git

**Consulta de refs:** 2026-10-28 15:11:56 UTC, `git ls-remote` somente leitura.
**Refs remotas confirmadas:** `main=22dca64556338a8fa9aaa89ce627a4f4af72317d`; `staging=fff85218fd71b164dc7465ca72d22b4a53232f49`.

## Relação das linhas

| Referência | SHA completo | Relação observada |
|---|---|---|
| `origin/main` | `22dca64556338a8fa9aaa89ce627a4f4af72317d` | Filho de `9b79751278496e51134a6ab8d495706bb2c700a7`; um commit exclusivo em relação a staging. |
| `origin/staging` | `fff85218fd71b164dc7465ca72d22b4a53232f49` | Merge de `26dc05862138b8643b01656ea2a6376eff0a189d` e `9b79751278496e51134a6ab8d495706bb2c700a7`; três commits exclusivos em relação a main. |
| Snapshot técnico auditado `e5bf3147...` | `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636` | Filho de `8a087fd5baa9e2eaa98bc1d2ed52b4a60f8c7036`; main é ancestral; não contém os três commits exclusivos de staging. |
| Auditoria documental B3 | `45fa5c5ff81982f7b784753e31a1dda0ce56cf5f` | Filho documental de `4805e3caab18f183c37375d23af1b2e12a425d1b`; não é uma release de aplicação. |
| Auditoria B4 | `7c72a837ea0e89a31e67b457130b019658561bb1` | Linha documental baseada em `45fa5c5...`; análise de compatibilidade e aprovação, sem promoção para branches remotas. |

`git rev-list --left-right --count`: `main...staging = 1/3`; `main...e5 = 0/21`; `staging...e5 = 3/22`. Merge-bases: main/staging `9b79751278496e51134a6ab8d495706bb2c700a7`; main/e5 `22dca64556338a8fa9aaa89ce627a4f4af72317d`; staging/e5 `9b79751278496e51134a6ab8d495706bb2c700a7`. A comparação `main` versus e5 mostra 113 arquivos, 13.459 inserções e 328 remoções.

## Compatibilidade por área

| Área | main `22dca...` | staging `fff852...` | Snapshot `e5bf...` | Divergência e risco |
|---|---|---|---|---|
| Configuração | `backend/settings.py` da linha main | Diff funcional em `backend/settings.py` relativo a e-mail local | Corresponde à regra estrita de main na comparação B4 | Pode afetar boot/preflight. Confirmar comportamento no ambiente e no baseline escolhido. |
| CI/CD | `ci-deploy.yml`; deploy exige dispatch explícito | Mesmo workflow/contrato de deploy, com ref staging | Acrescenta workflow experimental de homologação e ferramentas locais | Runs de push recentes construíram imagens, mas pularam deploy; não são runtime. |
| Schemas/índices | Linha remota base | Mesmo estado comum, exceto commits próprios; comparar schema em alvo antes de mudança | Contém adições de schema/índices e migrations auditadas em B2 | Não presumir que índices/migrations de e5 existem nos bancos dos ambientes. |
| Escritores/publicação/restore | Não contém todos os componentes editoriais de e5 | Não contém os commits técnicos do snapshot auditado no escopo B4 | Inclui serviços de publicações imutáveis, restore e alterações editoriais | Implementar contra e5 pode visar APIs que não existem no serviço de staging observado. |
| Atividades e progresso | Contratos anteriores ao snapshot | As três alterações exclusivas exigem revisão; Coolify deploy de staging aponta a fff | Inclui sessões, atividades, tentativas e alterações de progresso | Impacto pedagógico e de compatibilidade; ADR-002 e reconciliação obrigatórios. |
| Frontend | Linha remota main | Mesmo conteúdo base de aplicação em áreas comparadas pelo B4 | Variações em leitor, quizzes, hooks e contratos | Sem digest do frontend ativo, não se comprova compatibilidade API/UI. |
| Autenticação/roles | Linha main | Diferença específica e commits próprios devem ser revisados antes de código | e5 altera rotas, segurança/sessões em relação ao baseline remoto | Não inferir roles de produção pelo snapshot. |
| Importação/jobs/scripts | Documentação versionada define gates, não execução | Estado de staging observado não demonstra migrations aplicadas | e5 inclui alterações técnicas de import, gestão, testes e scripts | Writer indireto pode contornar futuro fencing; inventário precisa ser repetido contra a linha escolhida. |

O detalhe de compatibilidade estática consta em [B4 — branch compatibility](editorial-generations-phase-2-1a-12b4-branch-compatibility.md). Esta fase não fez merge, rebase ou comparação mutável.

## Confronto entre deployments Coolify e refs

| Recurso | Branch configurada (Coolify) | Registro Coolify mais recente relevante | Comparação com Git | Interpretação segura |
|---|---|---|---|---|
| `trilhacode-staging-api` | `staging`, seletor `HEAD` | Deployment concluído, SHA `fff852...` | Igual ao HEAD remoto de staging consultado | Proveniência do deployment registrado; digest/instância/rota não comprovados. |
| `trilhacode-staging-frontend` | `staging`, seletor `HEAD` | Deployment concluído, SHA `fff852...` | Igual ao HEAD remoto de staging consultado | Mesmo limite; ainda não é prova de imagem servida. |
| `trilhacode` em `general` | `main`, seletor `HEAD` | Deployment falho, SHA `22dca...` | Igual ao HEAD remoto de main consultado | Não identifica produção nem versão em execução. |

O run CI de main `40488544210` e o de staging `40394870286` tinham jobs de build bem-sucedidos e jobs de deploy `skipped`. O run de publicação GHCR `39179762892` utilizou `41dc470c567bae50b7ebcf0662d45d43863980c9`; não há associação demonstrada entre essa imagem e os deployments de staging posteriores.

## Recomendação de linha

| Objetivo | Recomendação condicional |
|---|---|
| Baseline implantado | Não escolher SHA para produção ou runtime de staging enquanto faltar digest ativo e associação com tráfego. |
| Validação técnica | Preservar `e5bf3147...` apenas como snapshot de auditoria/PoC. Para validar contra um alvo existente, primeiro pedir ao responsável a confirmação de que o recurso staging observado e seu deployment `fff852...` são o alvo pretendido. |
| Implementação | Preferir uma branch de integração dedicada derivada do baseline de release aprovado pelo responsável, seguida de reconciliação seletiva dos commits de e5 e dos três commits exclusivos de staging. Não escolher main, staging ou e5 automaticamente. |
| Release | Seguir a linha e os gates que o responsável confirmar; `DEPLOY.md:20–22` documenta a intenção de produção em main e staging em staging, mas não prova a operação atual. |

**Gate bloqueante:** o registro de deployment concluído em staging melhora a evidência disponível, mas não elimina a lacuna de runtime. Antes de código, vincular serviço/rota, imagem ativa por digest, build/proveniência e SHA; selecionar ambiente e baseline humano; reconciliar schema, contratos e migrations; reexecutar a auditoria de leitores/escritores na linha final.
