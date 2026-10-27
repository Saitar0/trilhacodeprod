---
arquivo_id: "f7-32-1-01-workflow-reprodutibilidade-quality-gates-p02-pratica-md"
parent_key: "32.1"
tipo_arquivo: "practice"
assunto: "01_workflow_reprodutibilidade_quality_gates"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Prove o bloqueio do quality gate

**Desafio:** demonstre a diferença entre executar CI e exigir seu resultado para integrar uma mudança.

**Passos:**
1. Execute o workflow em um PR de exercício e identifique o nome/contexto exato do status check produzido.
2. Configure ou inspecione a regra de proteção da branch de exercício para exigir esse check. Se não tiver permissão de configuração, use uma captura/registro da política existente ou uma simulação documentada da configuração esperada.
3. Em um commit isolado, faça um dos checks falhar de forma deliberada e segura; confirme que o resultado fica vermelho e que a política não permite integração enquanto o check obrigatório estiver pendente/falho.
4. Restaure a mudança, execute novamente e registre o resultado verde.
5. Se o repositório usa merge queue, confira se o workflow atende também ao evento `merge_group`.

**Evidências:** nome do check; configuração ou registro da proteção; execução falha e recuperação; indicação do que foi realmente observado e do que foi apenas simulado.

**Verificação:** compare o check selecionado na política ao check produzido; não conclua que o merge está bloqueado apenas por ver um job vermelho.

**Aceite:** falha é detectada; a regra exige o status check correto; limite de permissão ou ausência de branch protegida fica declarado sem ser apresentado como bloqueio verificado.

