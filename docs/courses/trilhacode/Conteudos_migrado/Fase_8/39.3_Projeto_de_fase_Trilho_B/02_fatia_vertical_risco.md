---
arquivo_id: "f8-39-3-02-fatia-vertical-risco-md"
parent_key: "39.3"
tipo_arquivo: "project_milestone"
ordem: 2
itens_origem: ["M2"]
titulo_marco: "Entrega 2 — Construir a fatia vertical e testar o risco central"
---


### Entrega 2 — Construir a fatia vertical e testar o risco central

Implemente o menor fluxo que atravessa persistência/API/processamento e prova o problema técnico. Quando a base mínima da Fase 5 for necessária, mantenha o schema entre duas e quatro tabelas com migrations e uma API autenticada simples. Limite autenticação e telas ao necessário para executar o cenário; não enfraqueça autorização para simplificar o teste.

| Tipo escolhido | Fatia e evidência mínima do problema central |
|---|---|
| **T1 — Transacional** | Ingressos/pedidos com reserva de estoque e pagamento simulado idempotente. Teste concorrência ou repetição e prove que não há venda além do estoque nem efeito duplicado. |
| **T2 — SaaS multiempresa** | Agenda de clínicas com tenant e papel. Teste negativo prova que uma clínica não lê nem modifica dados de outra, inclusive por identificador direto. |
| **T3 — Tempo real e colaboração** | Quadro/votação compartilhada. Teste com dois clientes autenticados prova atualização, reconexão e estado esperado após uma desconexão, sem permitir acesso não autorizado à conexão. |
| **T4 — Conteúdo, feed e busca** | Catálogo de receitas com paginação, filtros e ordenação definida. Testes cobrem limites, combinações de filtro, ordem estável e resposta quando não há resultados. |
| **T5 — Dados e processamento assíncrono** | Importador de vendas e relatório. Teste de arquivo sintético cobre validação, progresso/estado consultável, falha e repetição sem duplicar registros/efeitos. |

**Evidências:** migrations/schema, API ou job funcional, teste executável com saída salva, exemplo de entrada/resultado sintético, decisão sobre autorização/erros e limites conhecidos.


**Feedback:** se a demonstração exige explicar manualmente o resultado, transforme a hipótese em asserção automatizada ou procedimento passo a passo com saída esperada. Não atribua à aplicação garantias que o teste não verifica.

