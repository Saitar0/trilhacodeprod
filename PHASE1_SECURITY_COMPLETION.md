# Trilha Code — Fase 1.5: Segurança e validação

Data: 16/10/2026

## Status

**Fase bloqueada; não declarar conclusão de segurança.** As verificações do frontend funcionam, mas não foi possível obter uma auditoria npm atual, instalar/executar `pip-audit` nem iniciar MongoDB/Docker neste ambiente. Como consequência, não foi possível determinar com precisão o conjunto de versões corrigidas para todas as ocorrências e não foram alterados manifests/lockfiles com base em suposições. Nenhuma vulnerabilidade foi ignorada para liberar o CI.

## Vulnerabilidades encontradas

O relatório da Fase 1 registrou **13 advisories npm** (2 baixas, 4 moderadas, 5 altas, 2 críticas) em dependências associadas a ESLint, Vitest/Tinypool, AJV, Tailwind/PostCSS e transitivas relacionadas. A quantidade de advisories não representa quantidade de pacotes. O relatório não preservou os IDs, a saída JSON nem o vínculo advisory → pacote/versão; a execução atual de `npm audit --json` falhou antes de consultar o registry (`ENOTFOUND registry.npmjs.org`). Portanto não é possível reconstituir esses detalhes com confiança só a partir daquele total.

O relatório anterior registrou **18 entradas de advisories em dois pacotes Python**: PyMongo e Starlette. O comando pedido nesta fase não pôde ser executado porque `pip-audit` não está instalado. Como referência de atualização, o advisory atual do PyMongo define correção em 4.18.2; o advisory atual do Starlette define correção em 1.1.0. Isso informa o mínimo para esses advisories, mas não substitui a saída da auditoria original, cujos IDs exatos não foram preservados.

| Dependência | Versão no manifesto/lockfile | Vulnerabilidade/gravidade identificável | Direta ou transitiva | Correção recomendada | Compatibilidade / superfície |
|---|---:|---|---|---|---|
| PyMongo | 4.6.3 (produção) | 18 entradas Python foram reportadas em conjunto para PyMongo e Starlette; IDs individuais indisponíveis. O advisory atual conhecido é CVE-2026-96749 / GHSA-v4x9-3549-crwv, alta. | Direta em `requirements.prod.txt`; também dependência de Motor | PyMongo 4.18.2 ou posterior corrigido | Runtime. Validar com Motor antes de adotar. Motor 3.7.1 está presente no ambiente de desenvolvimento, mas a combinação de produção não foi instalada/validada.
| Starlette | 0.37.2 (restrição transitiva de FastAPI em produção) | 18 entradas Python foram reportadas em conjunto. Advisories atuais conhecidos incluem CVE-2026-48710 (moderada; corrigida em 1.0.1) e CVE-2026-48818 (alta; corrigida em 1.1.0). IDs não confirmados como os das 18 entradas originais. | Transitiva de FastAPI | 1.1.0 ou posterior corrigido, junto com FastAPI compatível | Runtime. Exige atualização coordenada de FastAPI, pois FastAPI 0.110.1 limita a faixa de Starlette. A combinação não foi instalada em Python 3.11 nem testada com MongoDB.
| FastAPI | 0.110.1 (produção) | Sem advisory próprio atribuído nos dados disponíveis; atualização necessária para liberar uma faixa segura de Starlette. | Direta | Atualizar em conjunto com Starlette; versão final pendente da resolução/instalação de dependências | Runtime. Pode alterar comportamentos de integração, OpenAPI e eventos de lifespan; imports da aplicação passam no ambiente local atual, não na combinação proposta.
| Motor | 3.3.1 (produção) | Não aparece como pacote vulnerável no resumo da auditoria anterior. | Direta | Manter Motor; validar versão compatível com PyMongo corrigido antes de piná-la | Runtime. Motor será mantido, como solicitado. A migração arquitetural do driver continua fora desta fase.
| Pydantic | 2.13.5 (produção) | Nenhuma vulnerabilidade foi atribuída no resumo disponível. | Direta | Manter até resultado completo de `pip-audit` | Runtime. Já é Pydantic v2; validar serialização e modelos sob a matriz Python 3.11 de produção.
| ESLint e dependências associadas | ESLint 9.23.0; pacote/advisories específicos não recuperáveis | Parte dos 13 advisories npm; severidade individual indisponível | ESLint direto; itens associados podem ser transitivos | Pendente da saída atual do audit; atualizar dentro da major 9 quando possível | Desenvolvimento/CI. Lint local passou com a árvore instalada.
| Vitest / Tinypool | Vitest 3.2.7 e Tinypool 1.1.1 no lockfile instalado | Parte dos 13 advisories npm; não foi possível confirmar IDs/gravidades a partir do audit original | Vitest direto de desenvolvimento; Tinypool transitivo | Pendente de compatibilidade Vitest/Tinypool confirmada pelo audit e registry | Desenvolvimento/CI. Um salto de major do Vitest pode exigir mudanças na configuração/testes.
| AJV | 8.17.1 direto e versões 6.x aninhadas no lockfile | Parte dos 13 advisories npm; versão/instância e advisory afetado não podem ser determinados pelo resumo anterior | AJV 8 direto; AJV 6 transitivo em ferramentas | Pendente do audit completo | Desenvolvimento/CI. A árvore tem múltiplas versões; elevar só o pacote direto não garante corrigir cópias transitivas.
| Tailwind CSS / PostCSS | Tailwind 3.4.17; PostCSS 8.5.28 | Parte dos 13 advisories npm; advisories individuais não recuperáveis | Ambos diretos de desenvolvimento; há dependências transitivas | Pendente do audit completo e resolução compatível | Desenvolvimento/build. Tailwind 4 seria major e requer migração de configuração; não aplicar sem verificar se um patch de Tailwind 3/transitiva resolve.

Os advisories atuais do PyMongo e Starlette acima são referências verificadas para orientar a atualização, não uma alegação de que correspondem a todas as entradas do relatório anterior. Também não foi possível obter, nesta execução, a lista completa dos advisories atuais.

## Alterações e versões

Não foram alterados dependências, manifests ou lockfiles nesta etapa. Os únicos valores “anterior/novo” são, portanto, **FastAPI 0.110.1 → pendente**, **Starlette 0.37.2 → pendente**, **Motor 3.3.1 → pendente**, **PyMongo 4.6.3 → 4.18.2 ou posterior recomendado, ainda não adotado**, e frontend sem alteração. Isso evita afirmar validação de combinações que não puderam ser instaladas ou auditadas.

Foi criado apenas este relatório. As alterações preexistentes do workspace foram preservadas.

## Validação

| Verificação | Resultado |
|---|---|
| `npm audit --json` | Bloqueada por DNS: `registry.npmjs.org` não resolveu (`ENOTFOUND`). Nenhum JSON de advisories foi recebido. |
| `pip-audit -r backend/requirements.prod.txt -f json` | Não executada: `pip-audit` não está instalado no ambiente. |
| `npm run typecheck` | Passou. |
| `npm run lint` | Passou. |
| `npm test` | Passou: 2 arquivos e 4 testes. |
| `npm run build` | Passou; Vite reporta chunk lazy de ícones de 799,58 KB. |
| `npm audit --audit-level=high` | Bloqueada pelo mesmo erro DNS; não é resultado aprovado nem reprovado por advisories. |
| Import da aplicação (`import server`) | Passou com os pacotes presentes no Python global local. Não prova que os pins de produção inicializam. |
| `python -m compileall -q backend` | Passou. |
| Coleta de testes backend | Passou: 47 testes coletados em `backend/`. |
| 47 testes backend com MongoDB | **Não executados.** MongoDB não responde em `127.0.0.1:27017`; Docker Desktop está instalado, mas acesso ao daemon foi negado. Nenhum banco existente foi acessado, criado ou apagado. |
| CI / deploy | Os dois jobs de deploy usam `needs: [backend, frontend]`. Qualquer falha nos jobs bloqueia os deploys. `pip-audit` e `npm audit --audit-level=high` são passos dos jobs necessários, então advisories acima do nível configurado continuam bloqueando deployment. Não foi consultada execução remota. |

Observação: o Python global é 3.13 e possui versões diferentes dos pins de produção (por exemplo FastAPI 0.141.1, Starlette 1.7.0, Motor 3.7.1 e PyMongo 4.17.0). O Dockerfile de produção usa Python 3.11. O import local, portanto, não valida a matriz de produção nem a correção atual do PyMongo.

## Docker e CI

O serviço MongoDB declarado no `compose.yaml` usa volume nomeado `mongo_data`; não foi iniciado para preservar dados e porque o daemon Docker não estava acessível. O CI cria MongoDB 7 como serviço temporário e executa a suíte backend. O fixture configura um nome `test_<uuid>`, recusa banco fora do prefixo `test_` e só remove o banco criado para aquela execução.

O workflow não condiciona deploy a uma saída artificial: os jobs de deploy dependem dos jobs backend e frontend, e falhas de auditoria fazem o job correspondente falhar. Lockfile npm existe e é usado por `npm ci` nos containers e no CI. O backend usa requirements fixados, sem lockfile de resolução completo; a atualização FastAPI/Starlette/Motor/PyMongo requer verificar resolução e build de imagem em CI.

## Riscos de regressão e Fase 2

- A atualização coordenada de FastAPI/Starlette pode afetar middleware, eventos `on_event` depreciados, serialização e OpenAPI.
- Atualizar PyMongo dentro da faixa suportada pelo Motor precisa validar leitura, escrita, BSON/serialização, autenticação e operações assíncronas.
- Vitest, ESLint e Tailwind devem ser atualizados conforme o caminho de menor impacto indicado pelo audit completo; major do Vitest ou Tailwind deve incluir revisão da configuração e dos testes.
- Os testes de autenticação/autorização, conteúdo, progresso, exercícios e serialização MongoDB permanecem sem resultado de execução nesta etapa por falta de serviço Mongo temporário.
- Após restabelecer rede e daemon MongoDB, repetir ambos os audits, registrar IDs por pacote/versão, atualizar dependências e lockfile, rodar comandos frontend, build de produção, pip-audit e os 47 testes em Mongo descartável no Python 3.11.
- Planejar para a Fase 2 a migração de handlers `on_event` para lifespan e, separadamente, avaliar a futura descontinuação arquitetural do Motor. Motor não foi substituído nesta fase.

## Fontes de advisories de referência

- [PyMongo CVE-2026-96749 / GHSA-v4x9-3549-crwv](https://github.com/advisories/GHSA-v4x9-3549-crwv)
- [Starlette CVE-2026-48710 / GHSA-86qp-5c8j-p5mr](https://github.com/advisories/GHSA-86qp-5c8j-p5mr)
- [Starlette CVE-2026-48818 / GHSA-wqp7-x3pw-xc5r](https://github.com/advisories/GHSA-wqp7-x3pw-xc5r)
