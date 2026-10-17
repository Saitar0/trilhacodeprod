# Roadmap técnico

Atualizado em 17/10/2026 a partir da branch padrão `main` (base da missão `27a98964`), código, workflows e resultados da CI. Status descrevem evidências observadas; homologação em staging permanece separada.

| Frente | Status | Evidência / prioridade | Próximo critério verificável |
| --- | --- | --- | --- |
| A — qualidade e confiabilidade | CONCLUÍDA | PR #9 protege o alvo Mongo dos testes com DB descartável/loopback e valida `compose.yaml` e `compose.qa.yaml` sem iniciar serviços. CI #18 e #29 passou nos jobs backend e compose. | Revalidar após integração da PR #9. |
| B — E2E | EM EXECUÇÃO | PR #12 usa Mongo service efêmero, seed e credenciais fictícias. O fluxo aluno (login, catálogo, completar tópico, persistência após reload, logout) passou na CI #23. A ponta atual acrescenta overflow 360/390 px e navegação admin read-only; CI #29 ainda está em execução. | CI verde na ponta atual e falhas de viewport corrigidas, se reproduzidas. |
| C — experiência/responsividade | EM EXECUÇÃO | PR #12 mede overflow horizontal no catálogo, detalhe da trilha e leitor em 360/390 px, aguardando dois frames após redimensionar. Nenhuma inspeção visual local foi possível; Docker não está disponível no ambiente. | Browser CI verde; investigar qualquer overflow reproduzido. |
| D — desempenho frontend | CONCLUÍDA | PR #10 substitui importação global de ícones pela resolução dinâmica sob demanda. Build: chunk do catálogo de ícones caiu de 799.578 B / 147,81 KiB gzip para 213.071 B / 50,78 KiB gzip (~65,7% menos bytes gzip nesse chunk); CI #19 passou. O build produz cerca de 1.593 chunks pequenos de ícones (~1,35 MB bruto somado), carregados conforme uso. | Monitorar quantidade de chunks/requisições em build e páginas com muitos ícones. |
| E — backend, segurança e integridade | EM EXECUÇÃO | PR #11 alinha leituras diretas com visibilidade pública; testes de regressão e CI #21 passaram. PR #13 adiciona validação 422 antes do planejamento para evitar exceções de formato/parcialidade em imports; CI #24 passou na revisão anterior, ponta corrigida aguarda CI #31. | CI #31 verde e revisão técnica independente final. |
| F — homologação funcional | PENDENTE | Nenhum banco/staging real foi acessado. PR #12 valida fluxos seedados em ambiente descartável; sem validação manual das demais rotas administrativas nem de edição/import persistente completa. | Planejar homologação funcional em ambiente isolado após aprovação de acesso e dados descartáveis. |
| G — staging/release | BLOQUEADA POR GATES | Planos e runbooks existentes foram lidos. G0 ainda depende do inventário e aprovações listados no checklist. Não há evidência recente suficiente para reproduzir `Host key verification failed`; não alteramos SSH, segredos, Coolify ou infraestrutura. Nenhum G3–G6 foi executado. | Responsável aprovar e realizar os gates operacionais individualmente; validar publicamente a configuração SSH sem expor ou alterar credenciais. |

## Backlog para outra missão

- Cobrir fluxos administrativos de escrita (edição, publicação, importação e versionamento) com fixtures descartáveis e critérios de cleanup.
- Validar acessibilidade por axe/teclado e inspecionar visualmente nos breakpoints 360/390 px quando houver navegador utilizável.
- Avaliar um limite automatizado de tamanho para entradas/chunks do bundle após observar um build estável.
- Reproduzir e investigar qualquer falha de import que não seja de estrutura JSON ou hierarquia.
- Executar homologação de release e gates G0–G7 somente com aprovação e infraestrutura/dados isolados.

## Segurança e escopo

Nenhuma credencial ou segredo foi consultado/registrado; nenhuma migração, seed ou escrita em Mongo real; nenhum deploy, webhook, restart, mudança Coolify/VPS, firewall/SSH ou ação sobre o Dev Forge. PRs continuam abertos para revisão, sem merge automático.