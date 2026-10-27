---
arquivo_id: "f5-24-1-01-escopo-doubles-unitarios-integracao-01-teoria"
parent_key: "24.1"
tipo_arquivo: "theory"
assunto: "01_escopo_doubles_unitarios_integracao"
ordem: 1
itens_origem: ["theory-container", "Microtópico 1 — Classifique pelo limite que o teste atravessa", "Microtópico 2 — Escolha dublês de teste pela pergunta", "Microtópico 3 — Testes unitários e integração respondem a riscos diferentes"]
---

## Teoria

## Microtópico 1 — Classifique pelo limite que o teste atravessa

Os nomes “unitário”, “integração” e “ponta a ponta” variam entre equipes. Para entender a confiança de um teste, descreva o que ele executa de verdade: quais componentes são reais, quais dependências foram substituídas, quais fronteiras atravessa e qual resultado observável verifica.

- **Unitário:** verifica uma unidade pequena de comportamento, normalmente sem iniciar serviços externos. Pode testar uma função, objeto ou regra; não precisa corresponder a uma classe por teste.
- **Integração:** verifica a colaboração entre partes que podem falhar juntas, como módulo Nest, controller e provider, ou aplicação e banco de dados. Deve usar as dependências reais relevantes à pergunta; outras fronteiras podem ser substituídas.
- **Ponta a ponta (E2E):** percorre um fluxo amplo pela interface ou entrada pública do sistema. Em uma API, pode iniciar a aplicação e enviar uma requisição HTTP. O escopo é mais amplo, mas não precisa conectar a todo fornecedor externo em cada execução.

Essas categorias não são uma hierarquia de valor. Um teste rápido de regra local não prova que SQL está correto; um teste com banco não prova que uma pessoa consegue concluir o fluxo; um E2E pode confirmar o caminho principal sem cobrir todas as combinações da regra. Combine escopos conforme os riscos e o custo de manutenção.

## Microtópico 2 — Escolha dublês de teste pela pergunta

Um dublê substitui uma dependência real durante um teste. Termos como stub, fake, spy e mock são usados de formas ligeiramente diferentes; deixe claro o papel que o dublê cumpre:

- **Stub:** fornece respostas controladas para o cenário, como um serviço de preços que retorna uma cotação conhecida.
- **Fake:** implementação simplificada que funciona, como um repositório em memória; não reproduz necessariamente toda semântica do banco real.
- **Spy:** registra chamadas a uma implementação ou função para observar o que aconteceu.
- **Mock:** substituição programada para controlar respostas e/ou verificar interações esperadas.

Substituir uma fronteira externa pode tornar o teste previsível, rápido e capaz de exercitar falhas difíceis de provocar. Mas se o objetivo é verificar uma constraint, uma transação, serialização, configuração de rota ou compatibilidade entre dois providers, mockar justamente a parte em questão elimina a evidência.

Prefira afirmar o resultado observável do comportamento. Verifique chamadas quando a interação fizer parte do contrato — por exemplo, garantir que uma cobrança não é enviada após uma validação rejeitada. Evite amarrar todo teste a detalhes internos como a ordem de chamadas entre métodos privados; isso causa falhas em refatorações que preservam o comportamento.

## Microtópico 3 — Testes unitários e integração respondem a riscos diferentes

Um teste unitário focado pode percorrer casos de uma regra de desconto sem subir o Nest nem acessar a rede. Dê entradas e observe resultados, erros ou efeitos relevantes. Use limites explícitos para valores, ausências, duplicatas e falhas. O isolamento facilita localizar defeitos, mas um fake pode divergir do banco ou API que representa.

Um teste de integração reduz essa incerteza ao usar componentes reais na fronteira que deseja verificar. Se a pergunta é se uma constraint única do PostgreSQL evita duplicidade, teste com PostgreSQL de teste/temporário, migrações aplicadas e dados controlados. Substituir o banco por um Map não prova o comportamento de SQL. Por outro lado, não é necessário abrir uma conexão de banco para cada caso de validação pura.

Diga exatamente qual parte é real e qual foi substituída. Em NestJS, o módulo de teste pode compor providers reais e substituir somente um provider específico. A classe TestingModule não torna o teste unitário automaticamente: importa o que foi inicializado e qual limite é exercitado.

