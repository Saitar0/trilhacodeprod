---
arquivo_id: "f9-44-1-90-integracao-kp01-feedback-pratica"
parent_key: "44.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_csharp_sdk_pipeline_api", "02_injecao_dependencia_persistencia"]
ordem: 1
itens_origem: ["P01"]
---


**Feedback de referência:** um `DbContext` scoped não deve ser injetado diretamente no construtor de serviço singleton; avalie tornar `OrderService` scoped/transient ou criar escopos de forma explícita conforme a necessidade. Use validação de escopo e testes que cruzem requisições.

**Erro comum:** considerar que o container resolve os lifetimes automaticamente sem consequência ou que `DbContext` é seguro para uso concorrente compartilhado.

