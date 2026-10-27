---
arquivo_id: "f5-23-3-01-complexidade-essencial-e-acidental-01-teoria"
parent_key: "23.3"
tipo_arquivo: "theory"
assunto: "01_complexidade_essencial_e_acidental"
ordem: 1
itens_origem: ["theory-container", "Microtópico 1 — Simples não significa improvisado", "Microtópico 2 — Complexidade tem custo dos dois lados"]
---

## Teoria

## Microtópico 1 — Simples não significa improvisado

Uma solução simples atende aos requisitos conhecidos com o menor conjunto de conceitos que o time consegue entender e manter. Ela não é necessariamente a solução com menos linhas nem autoriza ignorar segurança, testes, dados ou restrições já confirmadas.

Uma abstração pode ser útil mesmo antes de haver duas implementações quando protege uma regra central de um detalhe instável, oferece um limite de teste valioso ou reduz dependências difíceis de controlar. A contagem de implementações não é um critério suficiente. O inverso também é verdadeiro: separar uma função em interface, factory, adapter e módulo sem mudança provável ou teste habilitado pode apenas obrigar quem lê a percorrer mais arquivos.

Pergunte que trabalho concreto o desenho facilita hoje: compreender uma regra, trocar uma dependência, testar sem serviço externo, limitar efeitos colaterais ou acomodar uma variação já conhecida. Se a resposta depender somente de “vai escalar” ou “é padrão de mercado”, falta uma necessidade verificável.

## Microtópico 2 — Complexidade tem custo dos dois lados

**Complexidade acidental** é esforço introduzido pela forma da solução, como camadas redundantes, configuração sem uso, abstrações genéricas precoces ou conceitos duplicados. **Complexidade do problema** vem das regras reais, integrações, riscos, volume e restrições do domínio. Remover a primeira ajuda; fingir que a segunda não existe só a desloca para bugs e retrabalho.

Também existe custo de não criar uma fronteira: uma regra pode ficar espalhada, testes podem exigir banco e rede, ou uma mudança pode obrigar alterações em muitos módulos. Compare o custo total ao longo do uso esperado, incluindo entendimento, implementação, operação e reversão, em vez de premiar apenas o menor desenho inicial.

Exemplo: uma ferramenta interna tem um único formato de exportação estável. Criar uma plataforma de plugins para três formatos hipotéticos acrescenta contratos, registro, compatibilidade e testes. Se a segunda exportação for solicitada e houver uma variação real, introduzir uma estratégia naquele ponto pode ser mais claro. Se exportação exige conformidade regulatória ou troca externa custosa, uma fronteira pode justificar-se antes; a decisão depende do risco já conhecido.

