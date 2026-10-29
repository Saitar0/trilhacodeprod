# Beta 7.1 — classificação das relações curriculares

Fonte: `docs/beta/beta5-first-phase-manifest.json`, 30 relações extraídas; o contrato tipado preserva tipo e destino. A cópia de prévia persiste relações cujo destino está carregado na Fase 1 (21). As nove relações restantes apontam para unidades de fases não carregadas na prévia; portanto são referências externas pendentes de escopo, não destinos inválidos. Nenhuma foi convertida em pré-requisito novo.

| Origem | Tipo declarado | Destino | Classificação | Persistida na Fase 1 |
|---|---|---|---|---|
| 1.1 | Complementar | 1.2 — Ambiente de desenvolvimento | Interna à fase | Sim |
| 1.1 | Relacionado | Fase 3 — 7.3 Dados e comunicação | Referência externa legítima; fora do lote | Não |
| 1.1 | Relacionado | Fase 5 — 18.1 Estrutura | Referência externa legítima; fora do lote | Não |
| 1.2 | Pré-requisito | 1.1 — Computação e software | Interna à fase | Sim |
| 1.2 | Complementar | 2.1 — Terminal e navegação | Interna à fase | Sim |
| 1.2 | Relacionado | Fase 5 — 20.2 Segurança básica | Referência externa legítima; fora do lote | Não |
| 2.1 | Complementar | 1.2 — Ambiente de desenvolvimento | Interna à fase | Sim |
| 2.1 | Relacionado | 3.1 — Git local | Interna à fase | Sim |
| 2.2 | Pré-requisito | 2.1 — Terminal e navegação | Interna à fase | Sim |
| 2.2 | Relacionado | Fase 5 — 17.2 Depuração no servidor | Referência externa legítima; fora do lote | Não |
| 2.2 | Relacionado | Fase 4 — 10.1 Containerização | Referência externa legítima; fora do lote | Não |
| 2.2 | Relacionado | Fase 8 — 38.1 Sinais operacionais | Referência externa legítima; fora do lote | Não |
| 2.3 | Pré-requisitos | 1.1 — Computação e software | Interna à fase | Sim |
| 2.3 | Pré-requisitos | 2.1 — Terminal e navegação | Interna à fase | Sim |
| 2.3 | Complementar | 3.3 — GitHub | Interna à fase | Sim |
| 2.3 | Relacionado | Fase 5 — 20.1 Autenticação | Referência externa legítima; fora do lote | Não |
| 2.3 | Relacionado | Fase 7 — 34.1 Base de cloud | Referência externa legítima; fora do lote | Não |
| 3.1 | Pré-requisito | 2.1 — Terminal e navegação | Interna à fase | Sim |
| 3.1 | Complementar | 3.2 — Trabalho com histórico | Interna à fase | Sim |
| 3.2 | Pré-requisito | 3.1 — Git local | Interna à fase | Sim |
| 3.2 | Complementar | 3.3 — GitHub | Interna à fase | Sim |
| 3.3 | Pré-requisitos | 2.3 — Acesso remoto | Interna à fase | Sim |
| 3.3 | Pré-requisitos | 3.1 — Git local | Interna à fase | Sim |
| 3.3 | Complementar | 3.2 — Trabalho com histórico | Interna à fase | Sim |
| 3.3 | Relacionado | Fase 7 — 32.1 Automação | Referência externa legítima; fora do lote | Não |
| 3.4 | Pré-requisitos | 3.2 — Trabalho com histórico | Interna à fase | Sim |
| 3.4 | Pré-requisitos | 3.3 — GitHub | Interna à fase | Sim |
| 3.5 | Pré-requisitos | 3.1 — Git local | Interna à fase | Sim |
| 3.5 | Pré-requisitos | 3.2 — Trabalho com histórico | Interna à fase | Sim |
| 3.5 | Pré-requisitos | 3.3 — GitHub | Interna à fase | Sim |

Resultado: 21 relações internas persistidas, nove referências externas preservadas no contrato/manifests. Os destinos externos são identificados pelo caminho e âncora da fonte, mas não foram carregados nem verificados semanticamente nesta fase. O trabalho seguinte é resolver os destinos contra inventários curriculares aprovados e decidir se cada relação é contextual ou pré-requisito efetivo.
