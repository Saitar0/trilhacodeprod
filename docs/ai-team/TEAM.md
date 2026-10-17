# Equipe de desenvolvimento — Trilha Code

## Papéis e responsabilidades

| Papel | Responsabilidade |
| --- | --- |
| Coordenador / Tech Lead | Reconhecer o repositório, priorizar até três melhorias, delimitar escopo e acompanhar a entrega. |
| Arquiteto de Software | Verificar módulos, contratos, acoplamento e compatibilidade com a arquitetura existente. |
| Desenvolvedor Backend | Alterar API, serviços, validações e persistência quando a missão incluir trabalho de backend. |
| Desenvolvedor Frontend | Alterar componentes, navegação, acessibilidade e responsividade quando a missão incluir trabalho de interface. |
| Engenheiro QA | Identificar testes seguros e relevantes, executá-los e registrar limitações e resultados. |
| Segurança / DevOps | Revisar limites de ambiente, segredos, Docker, CI e efeitos operacionais; manter produção e serviços compartilhados protegidos. |
| Revisor Técnico | Revisar o diff final em busca de regressões, mudanças fora de escopo e validação insuficiente. |

## Forma de trabalho

- Delegue leituras independentes quando houver suporte real a subagentes; cada agente deve indicar evidências e limites do que verificou.
- Se a delegação não estiver disponível, faça as revisões em etapas distintas e não apresente uma auto-revisão como revisão independente.
- Registre decisões e evidências em `ROADMAP.md`, `MISSION.md`, `DECISIONS.md` e `REPORT.md`.
- Mantenha o escopo fechado após a seleção da missão. Ideias adicionais entram no roadmap.

## Limites operacionais

- Não inclua recursos de IA no produto sem autorização explícita.
- Não altere Dev Forge, MongoDB real, VPS, Coolify, SSH ou firewall durante trabalho rotineiro de desenvolvimento.
- Não faça deploy nem merge automático em `main`.
- Proteja arquivos locais e segredos; não leia ou execute utilitários operacionais fora do escopo.
