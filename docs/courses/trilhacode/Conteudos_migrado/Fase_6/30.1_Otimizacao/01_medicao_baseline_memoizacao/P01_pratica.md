---
arquivo_id: "f6-30-1-01-medicao-baseline-memoizacao-p01-pratica-md"
parent_key: "30.1"
tipo_arquivo: "practice"
assunto: "01_medicao_baseline_memoizacao"
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Faça um diagnóstico com baseline
**Objetivo:** escolher uma otimização com base em evidência da interação ou carregamento.

**Passos:**
1. Escolha uma tela e uma ação concreta que pareça lenta ou pesada; descreva o que a pessoa percebe.
2. Fixe dados, navegador, viewport e condições de execução; registre versão/build e se o cache está frio ou aquecido.
3. Colete um perfil com React Profiler ou o painel Performance do navegador e identifique o trecho que consome tempo.
4. Registre a métrica relevante em várias execuções e calcule uma referência comparável, como mediana e faixa observada.
5. Formule uma hipótese específica que conecte o gargalo observado à técnica que pretende experimentar.

**Dica:** “o app está lento” ainda não indica a causa. Separe carregamento de código, interação, renderização e espera de rede.

**Entrega:** registro do cenário, evidência do perfil, baseline e hipótese testável.

**Critérios de conclusão:** cenário pode ser repetido; métrica corresponde ao gargalo; hipótese prevê qual medida deve mudar.

