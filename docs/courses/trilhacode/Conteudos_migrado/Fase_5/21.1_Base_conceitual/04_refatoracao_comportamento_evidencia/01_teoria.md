---
arquivo_id: "f5-21-1-04-refatoracao-comportamento-evidencia-01-teoria"
parent_key: "21.1"
tipo_arquivo: "theory"
assunto: "04_refatoracao_comportamento_evidencia"
ordem: 4
itens_origem: ["Microtópico 4 — Refatore com comportamento e evidência"]
---

## Microtópico 4 — Refatore com comportamento e evidência
Refatorar é alterar a estrutura mantendo o comportamento observável que precisa ser preservado. Comece com um exemplo ou teste que caracterize esse comportamento; depois mova uma responsabilidade ou crie uma fronteira pequena; por fim, compare o resultado. Um teste específico pode ficar mais fácil porque a regra deixou de depender de HTTP, rede ou banco real. Isso é um sinal de melhora, não uma pontuação completa da arquitetura.

Escolha dublês de teste com cuidado. Uma implementação real pode oferecer maior fidelidade quando é rápida e viável; uma implementação falsa ou stub pode ser adequada para serviço lento, externo ou não determinístico. Mocks rígidos que verificam cada chamada podem acoplar teste à forma interna e quebrar quando o comportamento público não mudou.

Compare antes e depois usando a mesma mudança ou teste: que módulos precisam ser entendidos, quantos pontos mudam, que configuração foi criada e se novos conceitos ajudam quem mantém o código. Se a abstração adiciona navegação e indirection sem resolver custo identificado, simplifique.

**Exemplo:** antes, o teste de regra precisa instanciar controller, banco e e-mail; depois, o caso de uso recebe apenas o colaborador necessário e o teste verifica a decisão e seu resultado com uma dependência substituta apropriada.

**Erro comum:** declarar que a arquitetura ficou melhor apenas porque há mais interfaces, arquivos ou mocks, sem mostrar qual mudança ou teste ficou mais simples.

**Checagem:** qual comportamento continuou igual e que dificuldade observável diminuiu depois da refatoração?

