---
arquivo_id: "f5-20-3-03-limites-de-abuso-e-recursos-p03-pratica"
parent_key: "20.3"
tipo_arquivo: "practice"
assunto: "03_limites_de_abuso_e_recursos"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Proteção contra abuso de uma rota
**Objetivo:** desenhar limites que cobrem frequência e custo sem depender de uma única métrica.

**Passos:**
1. Selecione uma rota com impacto mensurável, como envio de arquivo, busca, OTP, geração de relatório ou envio a serviço externo.
2. Estime recursos consumidos por chamada e liste vetores de abuso e necessidades legítimas.
3. Defina dimensões de limitação, por exemplo identidade, operação, origem de rede confiável, tamanho e teto por período; justifique as escolhas.
4. Defina resposta quando excede o limite e como o contador funciona entre várias instâncias.
5. Simule usuário legítimo no limite e tentativa de abuso acima dele; revise proxy, cabeçalhos de origem e logs sem dados sensíveis.

**Dica:** não invente um número universal. Calibre parâmetros com volume esperado e risco do produto; trate o exemplo como ponto de partida, não política legal ou padrão para qualquer serviço.

