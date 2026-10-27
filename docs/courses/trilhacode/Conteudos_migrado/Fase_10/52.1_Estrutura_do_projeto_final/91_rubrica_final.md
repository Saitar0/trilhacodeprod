---
arquivo_id: "f10-52-1-r00"
parent_key: "52.1"
tipo_arquivo: "rubric"
ordem: 0
itens_origem: ["rubrica"]
escala_rubrica: "0–2"
---


## Rubrica final
Atribua 0, 1 ou 2 por critério. Aceite somente com pelo menos 13/16 pontos e nenhum zero nos critérios de produto, segurança, avaliação ou deploy; itens ainda não demonstrados permanecem pendentes mesmo quando a soma alcança o limiar.

| Critério | 0 — ausente | 1 — parcial | 2 — evidência suficiente |
|---|---|---|---|
| Continuidade e problema | projeto reiniciado ou necessidade não descrita | continuidade/problema parcial | evolução do Trilho A e problema/público claros |
| Escolha e avaliação de IA | IA sem necessidade ou sem critério | hipótese/casos incompletos | decisão justificada e avaliação reproduzível |
| Fluxo vertical | caminho ponta a ponta ausente | fluxo funciona com lacunas de estado/erro | interface, backend e dados integrados com evidência |
| Segurança e privacidade | autorização/segredo/dados sem controle | controles presentes sem cenários críticos | fronteiras, autorização, minimização e falhas verificados |
| Testes e confiabilidade | sem testes úteis | testes parciais ou integração não comprovada | comportamento normal, erro e limites cobertos por evidência adequada |
| Operação e observabilidade | sem medidas ou resposta | sinais ou procedimentos incompletos | falhas, latência e custo observáveis com runbook e limites |
| CI/CD e deploy | pipeline/deploy não demonstrados | execução parcial ou manual sem registro | pipeline e deploy AWS/Terraform demonstrados e repetíveis |
| Documentação e decisões | README/diagrama/ADR ausentes | documentação desatualizada/incompleta | execução, arquitetura, trade-offs, limitações e teardown claros |

**Interpretação:** 13–16 pontos com os critérios obrigatórios sem zero: pronto para aceite da fase; 9–12 pontos ou qualquer pendência crítica: corrigir e reapresentar; 0–8: retomar os marcos necessários. A rubrica não substitui os critérios do projeto nem declara experiência profissional ou senioridade.

