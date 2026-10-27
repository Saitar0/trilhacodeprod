---
arquivo_id: "f10-53-3-p03"
parent_key: "53.3"
tipo_arquivo: "practice"
assunto: "04_falhas_operacao_tradeoffs"
ordem: 3
itens_origem: ["P03"]
---


### Atividade 3 — Revisão de falhas e defesa do desenho
**Contexto e objetivo:** testar se a proposta continua compreensível e operável quando uma hipótese deixa de valer.

**Instruções:** analise três incidentes: banco indisponível por 2 minutos; pico 5 vezes maior que a média assumida; cache retorna destino antigo após atualização. Para cada um, descreva impacto, sinal de detecção, contenção, recuperação e métrica/log que ajudaria. Reavalie ao menos uma decisão do diagrama e prepare uma explicação oral de até cinco minutos, incluindo um trade-off e uma pergunta que faria ao entrevistador.

**Entrega:** tabela dos incidentes, desenho revisado e apresentação ou roteiro de defesa.

**Dica gradual:** trace primeiro a requisição afetada; depois identifique o componente que falhou e o efeito visível ao usuário. Não presuma que retry resolve indisponibilidade.


