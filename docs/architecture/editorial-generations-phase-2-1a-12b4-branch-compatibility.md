# Fase 2.1A.12B.4 — compatibilidade entre linhas Git

**Consulta:** 2026-10-28; somente leitura; SHAs completos abaixo.

## Referências e ancestralidade

| Referência | SHA | Observação |
|---|---|---|
| origin/main | 22dca64556338a8fa9aaa89ce627a4f4af72317d | Branch padrão remota |
| origin/staging | fff85218fd71b164dc7465ca72d22b4a53232f49 | Branch remota de staging |
| Snapshot auditado | e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636 | Objeto local; não foi tratado como remoto nem implantado |
| Documento B2 | 4805e3caab18f183c37375d23af1b2e12a425d1b | Documenta a auditoria técnica |
| Documento B3 | 45fa5c5ff81982f7b784753e31a1dda0ce56cf5f | Commit local documental baseado na auditoria |

Resultados de git rev-list --left-right --count:

| Comparação | Exclusivos à primeira referência | Exclusivos à segunda |
|---|---:|---:|
| main...staging | 1 | 3 |
| main...e5bf3147… | 0 | 21 |
| staging...e5bf3147… | 3 | 22 |

Merge-bases observados:

- main e staging: 9b79751278496e51134a6ab8d495706bb2c700a7.
- main e snapshot: 22dca64556338a8fa9aaa89ce627a4f4af72317d; main é ancestral do snapshot local.
- staging e snapshot: 9b79751278496e51134a6ab8d495706bb2c700a7; o snapshot não contém três commits exclusivos de staging.

45fa5c5… é documental: a comparação de backend, frontend, .github, ops e Compose entre esse commit e e5bf3147… não mostrou diferenças. O snapshot local não foi publicado, mesclado ou comprovado como implantado nesta fase.

## Matriz de compatibilidade por área

| Área | main | staging | Snapshot e5bf3147… | Divergência e risco para integração |
|---|---|---|---|---|
| Autenticação e autorização | Linha remota vigente em 22dca645… | Mesma base comum, mais commits próprios | Inclui alterações adicionais em rotas de autenticação, segurança, sessões e permissões | Não portar integração de sessão/geração sem comparar contratos, cookies, roles e migrações contra o baseline aprovado |
| Configuração | backend/settings.py valida configuração SMTP em staging mesmo com transporte local | backend/settings.py dispensa essa validação quando email_transport == local | Corresponde à regra estrita observada em main | Diferença funcional pequena, mas capaz de afetar boot/preflight de staging |
| CI e workflows | Inclui workflow de validação foundation no HEAD consultado | A árvore difere no workflow foundation e contém três commits exclusivos | Adiciona workflow experimental MongoDB da PoC e arquivos de harness | Não confundir workflow da PoC com deploy nem incluir workflow local não reconciliado |
| Schemas e índices Mongo | Sem o conjunto de mudanças técnicas do snapshot | A comparação de áreas técnicas com snapshot aponta divergências | Altera indexes.py, schemas e integridade; adiciona índices/coleções auxiliares | Índices e contratos BSON podem não existir no runtime atual; exige diff por campo/índice e plano compatível |
| Writers editoriais | CRUD legado descrito na auditoria B2 | Árvore de conteúdo quase igual a main, mas objetos exclusivos ainda precisam de inspeção para qualquer implementação | Serviços de tracks/nodes/blocks/relations/imports/versions modificados; publicação imutável experimental adicionada | O snapshot cobre mais comportamento, mas não é baseline de release; writers legados podem contornar a geração |
| Leitores públicos | Leitura legada de coleções vivas | Sem diferença ampla identificada com main nos caminhos auditados | Rotas de atividades, progresso, sessões e componentes de leitura evoluídos | Troca de leitor exige contract tests por branch e comprovação do frontend efetivamente servido |
| Publicação | Workflow e procedimentos documentados; runtime não comprovado | Configuração declarativa pretende staging em staging | Serviço de publicações imutáveis e PoC coexistem com legado | CAS de publicação não elimina janela nos documentos vivos nem inconsistência da revisão de origem |
| Restauração | Legado de snapshots | Três commits exclusivos não foram reconciliados ao snapshot | Serviços de versões/restore e testes foram alterados, mas restore permanece serviço real separado da PoC | A implementação futura precisa conciliar jobs, leases e restore do ramo selecionado; não assumir equivalência |
| Importação | Linha remota anterior às alterações de snapshot | Difere por commits de staging não contidos no snapshot | services/imports.py, payload e rotas foram significativamente alterados | Import é writer crítico; incorporar/fencear antes de habilitar publicação |
| Atividades e quizzes | Contratos antigos relativos ao snapshot | Mudanças de staging não integralmente linha-a-linha nesta fase | Adiciona evaluator, publicações, rotas e tentativa versionada | Não inferir que as APIs do snapshot estão no servidor; preservar published_version_id e semântica legada até reconciliação |
| Progresso, submissions e notas | Dados legados; progresso não globalmente fixado por geração conforme B2 | Base comum de app, diferenças exclusivas precisam ser comparadas antes do código | Mudanças em progress, submissions, sessions e testes; dados de progresso ainda têm limitações de geração descritas na auditoria | Risco de órfão ou avaliação contra versão diferente; decisão ADR-002 obrigatória |
| Frontend e cache | Versão remota associada à main | main/staging selecionados têm a mesma base app nos caminhos examinados | Hooks, types, reader e atividades mudaram; cache da auditoria não era keyed pela geração | e5 não prova frontend implantado; qualquer token de geração precisa compatibilidade multi-request e invalidação |
| Testes | Runs de CI existem para SHAs das branches | Run de CI existe para SHA de staging | Adiciona grande suíte backend/frontend e PoC, incluindo regressões de atividades | Testes de uma linha não certificam outra; exigir matriz de compatibilidade e contrato nos SHAs alvo |
| Scripts e operações | DEPLOY.md documenta migrações/índices por gates | Configuração operacional real não observada | Adiciona ferramentas de homologação e runners de build | Scripts não equivalem a migration executada; confirmar quais migrations/índices foram aplicados via evidência autorizada |
| CI/CD e imagem | CI em main; deploy webhook só em dispatch explícito documentado | CI de push em staging; deploy condicional | Workflow experimental adicional; não observado deploy do snapshot | CI verde confirma checks; não prova build implantado, tag de imagem ativa ou saúde do serviço |

### Interpretação das diferenças

O diff remoto main versus staging mostrou apenas backend/settings.py e .github/workflows/foundation-validation.yml nas árvores comparadas. O diff do snapshot contra main é amplo: 113 arquivos, 13.459 inserções e 328 remoções na comparação técnica registrada. O staging tem três commits que o snapshot não contém, e o snapshot tem 22 commits não presentes em staging.

A tabela descreve riscos de compatibilidade, não uma afirmação de que toda mudança diverge semanticamente. As referências detalhadas de escritores, leitores, testes e riscos estão em [auditoria B2](editorial-generations-phase-2-1a-12b2-audit.md), especialmente seções 2–7. Os oito ADRs de B3 continuam a ser propostas.

## Alternativas de linha técnica

| Opção | Vantagens | Riscos e reconciliação | Avaliação |
|---|---|---|---|
| A — partir de main | Linha padrão remota e destino de release descrito em DEPLOY.md para produção | Não há prova que o SHA esteja implantado; não contém as alterações técnicas auditadas. Importar o trabalho de e5 exigiria seleção/revisão de commits e compatibilidade | Não basta escolher automaticamente |
| B — partir de staging | Branch remota que serve de referência declarada para staging | Não se comprovou que staging roda esse SHA; contém três commits não contidos no snapshot; efeitos de schema e fluxos precisam ser comparados | Adequada somente após baseline e reconciliação |
| C — partir do snapshot e5 | Código da auditoria, testes e PoC coerentes entre si; main é ancestral | Objeto local, alterações não integradas em main/staging e sem prova de build/deploy; alto risco de implementação contra API não servida | Bom baseline de análise/validação, não candidato automático a release |
| D — linha de integração específica reconciliada | Permite escolher um commit de origem comprovado e portar mudanças selecionadas com revisão explícita; evita merge implícito | Exige decisão humana, plano de integração, testes cruzados, inventário de migrations/índices e owner por conflito | Recomendação condicional preferida |

## Recomendação condicional

1. **Baseline implantado:** não comprovado; obter evidência de nível 1 por ambiente.
2. **Baseline de validação arquitetural:** manter e5bf3147… como snapshot de referência da auditoria/PoC, sem alegar implantação.
3. **Baseline para implementação:** não escolher até o responsável aprovar a relação entre imagem atual, main, staging e commits do snapshot. Em seguida, criar uma linha de integração isolada a partir do baseline de release aprovado e reconciliar mudanças selecionadas do snapshot por revisão de código — sem merge automático nesta fase.
4. **Linha de release pretendida:** a documentação versionada aponta produção para main e staging para staging, mas a configuração efetiva e a política atualmente operada devem ser confirmadas pelo owner.

## Gate bloqueante

Antes de qualquer mudança de runtime, registrar a decisão do ADR-008 com: ambiente-alvo; SHA/digest atualmente implantado; SHA de base de desenvolvimento; commits/arquivos portados; migrations e índices compatíveis; testes executados nos SHAs reconciliados; e owner que autoriza cutover. A mera existência de HEAD remoto ou run de CI não fecha este gate.
