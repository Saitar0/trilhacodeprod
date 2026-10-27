---
arquivo_id: "f6-29-2-03-flakiness-e-evidencia-p03-pratica-md"
parent_key: "29.2"
tipo_arquivo: "practice"
assunto: "03_flakiness_e_evidencia"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Investigue e estabilize um teste intermitente
**Objetivo:** substituir sincronização temporal frágil por condições verificáveis.

**Passos:**
1. Use um teste existente que dependa de `sleep`, seletores internos ou dados compartilhados, ou crie uma falha controlada de latência.
2. Identifique qual evento observável indica que a interface está pronta para a próxima ação.
3. Troque a pausa ou seletor frágil por locator semântico e assertion que aguarde essa condição.
4. Garanta que cada execução tenha dados próprios e limpe estado de rede, browser e backend conforme necessário.
5. Execute o caso repetidamente, inclusive em paralelo se a infraestrutura permitir, e registre as causas removidas e os limites que continuam externos.

**Dica:** não esconda um problema aumentando timeouts sem entender se ele vem de espera errada, serviço lento ou dado compartilhado.

**Entrega:** teste estabilizado e nota com causa, ajuste aplicado e evidência coletada.

**Critérios de conclusão:** a sincronização depende de estado observável; a execução não depende de ordem; problemas externos são identificados em vez de mascarados.

