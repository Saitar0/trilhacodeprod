---
arquivo_id: "f5-23-3-02-evolucao-reversivel-com-evidencia-01-teoria"
parent_key: "23.3"
tipo_arquivo: "theory"
assunto: "02_evolucao_reversivel_com_evidencia"
ordem: 2
itens_origem: ["Microtópico 3 — Evoluir requer feedback e uma rota de volta", "Microtópico 4 — Decida com evidências e revise"]
---

## Microtópico 3 — Evoluir requer feedback e uma rota de volta

Design evolutivo significa ajustar a estrutura conforme o entendimento e as necessidades mudam; não significa codificar sem direção e esperar que a arquitetura apareça sozinha. Pequenos passos precisam de feedback: testes que protejam comportamento, revisão de código, integração frequente, observação do sistema e conversa com quem define os requisitos. Sem essas condições, refatorar pode tornar mudança insegura.

Uma decisão sob incerteza pode ser adiada ou feita de forma reversível. Reversibilidade é a facilidade e o custo de trocar uma escolha quando chega informação nova; não é promessa de que qualquer arquitetura poderá mudar sem esforço. Um experimento isolado, um adapter pequeno, configuração explícita ou migração gradual podem reduzir o custo de aprendizagem. Já um contrato público consumido por vários sistemas, dados gravados em formato incompatível ou dependência de fornecedor podem tornar a escolha difícil de reverter.

Não trate “YAGNI” como proibição de planejamento. Evite implementar capacidade futura sem evidência, mas investigue agora riscos que seriam caros, irreversíveis ou bloqueadores de uma entrega. Um protótipo descartável ou uma decisão arquitetural curta podem responder à dúvida sem construir a solução completa.

## Microtópico 4 — Decida com evidências e revise

Uma boa decisão registra contexto, alternativas consideradas, escolha, consequências e gatilhos de revisão. Isso ajuda a distinguir “a opção escolhida falhou” de “o contexto mudou”. A nota pode ser curta; não precisa virar documento burocrático.

Exemplos de gatilhos mensuráveis: uma segunda integração real precisa do mesmo contrato; testes de uma regra ficam lentos porque sempre inicializam o banco; uma mudança de requisito se repete em três lugares; o volume ultrapassa um limite acordado; uma restrição regulatória passa a exigir retenção específica. Gatilhos devem refletir o problema, não criar métricas decorativas.

Ao simplificar uma arquitetura existente, proteja primeiro o comportamento que precisa permanecer. Faça uma alteração local, rode verificações relevantes, revise o diff e mantenha uma forma de recuperar a versão anterior. Remover uma camada útil pode acoplar o domínio à infraestrutura; preservar uma camada vazia pode tornar a mudança ainda mais cara. A decisão deve ser julgada por seus efeitos, não pelo prestígio do padrão.

