# Fase 2.1A.12B.4B — roteamento e atendimento

**Observação Coolify:** 2026-10-28, aproximadamente 15:35 UTC. A consulta foi limitada a metadados não sensíveis das aplicações identificadas.

## Classificação por serviço

| Serviço | Rota configurada | Rota ativa vinculada ao serviço | Tráfego atendido | Evidência e limite |
|---|---|---|---|---|
| API de staging (`skmrkg3jb1ifhx0qwwneeirx`) | Sim: campo de domínio/FQDN presente no detalhe da app; valor omitido | NÃO COMPROVADO | NÃO COMPROVADO | A configuração da aplicação não demonstra a regra atualmente carregada no proxy nem associação ao container observado. |
| Frontend de staging (`dcdudgprerqp8wbmgcxvfwmt`) | Sim: campo de domínio/FQDN presente; valor omitido | NÃO COMPROVADO | NÃO COMPROVADO | Mesmo limite; `docker_compose_domains` vazio/ausente não substitui metadados do proxy. |
| Candidato `trilhacode` no projeto `general` (`xm3mpex5rerhlbbuydpwf5wa`) | Nenhum FQDN observado | NÃO COMPROVADO | NÃO COMPROVADO | Não há evidência para classificá-lo como produção ou como destino de rota pública. |

## Saúde, readiness e tráfego

As duas apps de staging foram reportadas pelo Coolify como `running:healthy`, com `container_present=true` e `server_status=true`, mas `health_check_enabled=false`. Assim:

* `running:healthy` é registrado como status administrativo retornado pela plataforma, não como probe de aplicação independente.
* Liveness e readiness da aplicação não foram comprovados por healthcheck habilitado.
* Disponibilidade da rota ativa não foi comprovada.
* Atendimento real de tráfego não foi comprovado.

Não houve consulta DNS, requisição HTTP, probe, teste sintético, logs de acesso, proxy, servidor, terminal de container ou tráfego de usuários. Essa limitação é intencional conforme a autorização.

## Evidência necessária para fechar a cadeia

Um administrador autorizado deve fornecer apenas uma extração sanitizada dos metadados atuais do proxy/orquestrador: identificador da regra, hostname redigido ou identificador estável de domínio, serviço de destino, estado carregado, deployment/container associado e horário UTC. Para afirmar tráfego atendido, é necessária uma evidência agregada e sem dados pessoais que demonstre encaminhamento bem-sucedido para aquele serviço no intervalo observado. Configuração, status de container e último deployment não bastam.

Consulte o [pedido ao administrador](./editorial-generations-phase-2-1a-12b4b-admin-evidence-request.md) e a [matriz](./editorial-generations-phase-2-1a-12b4b-traceability-matrix.md).
