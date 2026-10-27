---
arquivo_id: "f5-24-2-02-integracao-rota-e-persistencia-kp02-gabarito-pratica"
parent_key: "24.2"
tipo_arquivo: "answer_key_pratica"
assunto: "02_integracao_rota_e_persistencia"
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** módulo Nest inicializado com componentes da rota e adapter real; banco exclusivo com migrations; primeira requisição cria uma linha, segunda viola a constraint e é traduzida para resposta prevista sem duplicar dados; payload inválido é rejeitado antes da persistência. O setup garante limpeza e não aceita conexão de produção.

