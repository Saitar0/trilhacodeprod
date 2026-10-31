# Solicitação sanitizada de evidências — baseline runtime Trilha Code

**Destinatário:** administrador autorizado da infraestrutura.
**Finalidade:** fechar a cadeia ambiente → rota → serviço/container ativo → imagem/digest → build → commit, para revisão do ADR-008.
**Escopo:** responder somente para os serviços de API e frontend de staging e para qualquer serviço que o administrador consiga identificar explicitamente como produção. Não presumir que o recurso `trilhacode` do projeto `general` seja produção.

Por favor, forneça os campos abaixo como metadados sanitizados, observados no mesmo intervalo UTC. Não envie exports completos do Coolify, logs brutos nem dados de configuração sensíveis.

## Por ambiente e serviço

1. Nome sanitizado do ambiente e identificador não secreto do ambiente.
2. Nome sanitizado do serviço e identificador não secreto do recurso.
3. Deployment atualmente associado ao serviço: ID, estado e horário UTC.
4. Identificador sanitizado do container/instância ativa e evidência de que pertence ao deployment indicado.
5. Referência OCI completa da imagem atribuída ao container (registry/repository/tag, se existir) e digest imutável efetivamente associado ao runtime.
6. Digest do artefato no registry, distinguindo digest de índice multi-arquitetura de digest de manifesto por plataforma.
7. Build/run que produziu exatamente esse digest, com job ID, repositório e SHA Git completo de origem.
8. Evidência verificável de proveniência/attestation, se existente, e indicação se o commit é uma declaração de label ou atestado verificável.
9. ID da rota/regra do proxy, domínio redigido ou identificador estável, serviço de destino e estado da regra carregada.
10. Evidência agregada e sem dados pessoais de que a rota encaminhou tráfego para esse serviço no intervalo observado. Não enviar IP, cookies, headers, payloads ou logs de requisições.
11. Estado reportado do processo, healthcheck e readiness, indicando a fonte e o horário UTC. Se não houver readiness separado, informar isso explicitamente.
12. Horário UTC comum da coleta e sistema/interface de onde cada campo foi obtido.

## Não enviar

Senhas, tokens, cookies, headers de autenticação, secrets, conteúdo de `.env`, variáveis de ambiente completas, chaves, URI autenticada, dumps de banco, dados de alunos, conteúdo pedagógico, logs brutos ou exportação integral do Coolify.

Se algum dado exigir permissão operacional privilegiada, o administrador autorizado deve consultar a fonte e retornar apenas os campos mínimos acima, sanitizados. Esta solicitação não autoriza comandos no host/container, alterações de infraestrutura, deploy, restart, probe, acesso a banco ou mudança de configuração.

## Como a resposta será usada

As evidências serão classificadas separadamente como runtime, proveniência, rota e tráfego. Um digest de build sem vínculo ao container permanecerá somente `CONFIRMADO_BUILD`; um domínio configurado sem regra ativa permanecerá `CONFIGURACAO_OBSERVADA`. O ADR-008 continuará `Proposed` e `PENDING_APPROVAL` até decisão humana explícita.
