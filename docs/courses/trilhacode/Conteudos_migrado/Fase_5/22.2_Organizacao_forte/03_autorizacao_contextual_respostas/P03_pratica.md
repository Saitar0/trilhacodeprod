---
arquivo_id: "f5-22-2-03-autorizacao-contextual-respostas-p03-pratica"
parent_key: "22.2"
tipo_arquivo: "practice"
assunto: "03_autorizacao_contextual_respostas"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Recurso protegido e resposta permitida
**Objetivo:** combinar a fronteira de rota com autorização contextual e saída mínima.

**Passos:**
1. Escolha um recurso pertencente a usuário ou tenant.
2. Proteja a rota de forma geral e, no serviço/política contextual, valide ação e propriedade do recurso em cada operação relevante.
3. Defina schema ou DTO de saída com somente os campos necessários.
4. Teste proprietário, outro tenant e papel privilegiado conforme regras; verifique que campo interno não aparece na resposta.
5. Documente qual camada rejeita formato, qual bloqueia rota, qual verifica o objeto e qual controla a saída.

**Dica:** autorização por papel e por objeto respondem a perguntas diferentes. Um UUID difícil de adivinhar não substitui a checagem de propriedade.

