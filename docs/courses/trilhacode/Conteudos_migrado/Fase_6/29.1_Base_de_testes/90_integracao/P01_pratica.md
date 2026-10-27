---
arquivo_id: "f6-29-1-90-integracao-p01-pratica-md"
parent_key: "29.1"
tipo_arquivo: "practice"
assuntos: ["01_consultas_semanticas", "03_interacao_assincrona", "04_isolamento_assertions"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Teste o contrato de um formulário
**Objetivo:** verificar validação, interação e confirmação usando a interface pública.

**Passos:**
1. Escolha um formulário de cadastro ou perfil com pelo menos dois campos e uma regra de validação observável.
2. Renderize o componente no ambiente de teste já usado pelo projeto e localize controles por label e botões por papel e nome.
3. Tente enviar dados inválidos e verifique a mensagem e o foco ou orientação esperados.
4. Preencha dados válidos usando interação de usuário, envie e confira a confirmação visível.
5. Torne temporariamente uma regra de validação inoperante para confirmar que o teste falha; restaure a regra e mantenha a assertion que detecta o defeito.

**Dica:** não chame a função de submit diretamente. O objetivo é passar pelo mesmo controle que uma pessoa usaria.

**Entrega:** testes para validação, submissão válida e confirmação, com uma nota sobre a falha introduzida e detectada.

**Critérios de conclusão:** testes encontram controles semanticamente; cobrem resultado válido e inválido; falham quando a regra importante é removida.

