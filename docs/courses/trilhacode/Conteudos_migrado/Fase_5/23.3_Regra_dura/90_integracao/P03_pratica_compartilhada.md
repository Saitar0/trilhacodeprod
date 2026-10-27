---
arquivo_id: "f5-23-3-90-integracao-p03-pratica-compartilhada"
parent_key: "23.3"
tipo_arquivo: "practice"
assuntos: ["01_complexidade_essencial_e_acidental", "02_evolucao_reversivel_com_evidencia"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Refatore em passos seguros

**Desafio:** uma classe mistura regra de desconto e chamada direta a um serviço externo de preços. A equipe discute se deve inserir uma interface, um adapter e um módulo antes de mudar o comportamento.

**Passos:**
1. Registre o comportamento existente com exemplos de entrada e resultado, incluindo erro ou indisponibilidade externa.
2. Identifique o motivo concreto para mudar a dependência: teste, substituição, política de domínio ou falha operacional.
3. Proponha uma alteração em etapas pequenas, indicando qual etapa pode ser revertida isoladamente.
4. Após a alteração, compare resultados antigos e novos para as mesmas entradas.
5. Registre o que ficou mais simples, o que ficou mais complexo e qual evidência justificaria outra mudança.

**Dica:** a primeira etapa pode ser somente extrair um limite nomeado e preservar o comportamento; não precisa introduzir de uma vez a arquitetura final.

