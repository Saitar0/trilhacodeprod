---
arquivo_id: "f10-52-1-scp"
parent_key: "52.1"
tipo_arquivo: "project_scope"
ordem: 0
itens_origem: ["Escopo e princípios"]
---


## Escopo e princípios
Este é o Trilho A. Continue a ideia escolhida em 3.5 e as versões construídas nas fases; não recomece do zero. A aplicação deve resolver uma necessidade concreta do usuário. Antes de implementar IA, descreva o fluxo atual, o problema e o resultado mensurável que a funcionalidade pretende melhorar. Se uma tecnologia ou capacidade da lista da trilha não atende a uma necessidade real do produto, registre-a como experimento isolado em `experiments/`, com hipótese, método, resultado e limitações; não a force no caminho principal.

Defina uma fatia vertical que atravesse interface, backend e dados. Use RAG, tool calling ou combinação somente quando fizer sentido ao caso. A aplicação mantém autorização fora do modelo, valida entrada e saída, protege documentos e credenciais, impõe limites de custo/latência e informa falhas de modo compreensível. Citações devem apontar para conteúdo realmente recuperado e acessível; ações de ferramenta usam identidade e permissões da sessão e confirmação quando o risco exigir.

Implemente em incrementos pequenos e revisáveis: requisito/ADR, fluxo funcional, testes e avaliação, tratamento de falhas, métricas, pipeline/deploy e documentação. Backend, banco, cache, fila, IaC e cloud entram no produto quando necessidade e fases anteriores justificam; capacidades requeridas para demonstrar o percurso da trilha podem ser mantidas em experimentos documentados. O critério de conclusão da Fase 10 pede deploy AWS e Terraform para demonstrar o percurso, portanto inclua a implantação isolada e controlada mesmo quando não for arquitetura do produto em produção.

