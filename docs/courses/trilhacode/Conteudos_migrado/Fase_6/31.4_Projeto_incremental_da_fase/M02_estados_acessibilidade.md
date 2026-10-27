---
arquivo_id: "f6-31-4-m02-estados-acessibilidade-md"
parent_key: "31.4"
tipo_arquivo: "milestone"
ordem: 2
itens_origem: ["M02"]
titulo_marco: "Marco 2 — Complete estados e acessibilidade do fluxo"
---

### Marco 2 — Complete estados e acessibilidade do fluxo
**Objetivo:** tornar o comportamento da fatia compreensível em todos os estados relevantes.

**Tarefas:**
1. Implemente e documente como reproduzir carregamento, sucesso com dados, sucesso vazio, erro e nova tentativa.
2. Inclua retry manual ou automático somente quando o contrato tornar a repetição segura; não repita escrita não idempotente cegamente.
3. Defina o texto e a ação disponível em cada estado, distinguindo falta legítima de dados de falha da API.
4. Verifique teclado, ordem e visibilidade do foco, labels dos controles e anúncio compreensível das atualizações.
5. Confirme que filtros, seleção ou contexto necessários não desaparecem após uma atualização ou erro recuperável.

**Evidências:** matriz estado → causa → mensagem → ação, demonstração ou capturas dos cinco estados e roteiro de teclado/foco.

**Verificação:** provoque os cenários com handlers ou fixtures controladas; confirme separadamente o fluxo real feliz contra a API de teste. Cada evidência deve dizer se o servidor foi simulado ou real.


