---
arquivo_id: "f2-5-1-01-regras-seletores-cascata-05-gabarito-pratica-guiada"
parent_key: "5.1"
tipo_arquivo: "answer_key_pratica"
assunto: "01_regras_seletores_cascata"
ordem: 1
itens_origem: ["P1"]
---

**Solução comentada:** a cor final é `#075`, porque `#status` tem maior especificidade que as classes e o seletor de elemento. A última regra `.aviso` não vence o ID. Para obter `#a00` com uma única alteração, mude o valor na regra `#status` para `#a00`. Evite aumentar especificidade sem necessidade. Confirme no painel de estilos qual declaração está ativa e quais foram sobrescritas.

**Erro comum:** dizer que a última regra sempre vence. A ordem é critério de desempate, não substitui a comparação de prioridade e especificidade.

