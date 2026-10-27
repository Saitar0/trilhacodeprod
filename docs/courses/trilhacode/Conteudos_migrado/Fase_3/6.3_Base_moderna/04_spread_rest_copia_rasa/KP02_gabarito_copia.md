---
arquivo_id: "f3-6-3-04-spread-rest-copia-rasa-kp02-gabarito-copia"
parent_key: "6.3"
tipo_arquivo: "answer_key_pratica"
assunto: "04_spread_rest_copia_rasa"
ordem: 2
itens_origem: ["P2"]
---

**Gabarito:** título original continua `"Aula"`; título da cópia vira `"Revisão"`; `meta.concluida` fica `true` nos dois, pois ambos apontam para o mesmo objeto interno. Para este formato conhecido: `const copiaSeparada = { ...original, meta: { ...original.meta } };`. Isso separa um nível específico, não faz cópia profunda arbitrária.

