---
arquivo_id: "f5-22-1-03-testes-da-composicao-nest-01-teoria"
parent_key: "22.1"
tipo_arquivo: "theory"
assunto: "03_testes_da_composicao_nest"
ordem: 3
itens_origem: ["Microtópico 5 — Teste o módulo e substitua a dependência certa"]
---

## Microtópico 5 — Teste o módulo e substitua a dependência certa
O pacote de testes do Nest pode criar um TestingModule com controllers, providers e imports semelhantes aos metadados de runtime. Para testar uma regra isolada, substitua o provider que atravessa a fronteira relevante por uma implementação de teste apropriada. Isso permite verificar o comportamento sem iniciar banco, rede ou framework HTTP quando eles não fazem parte da pergunta do teste.

Também teste integração quando o grafo, a configuração de módulos e o transporte forem parte do comportamento desejado. Um teste unitário com todos os colaboradores substituídos pode passar mesmo se os módulos reais estiverem conectados incorretamente. Separe a pergunta do teste: regra da aplicação, resolução de DI, ou fluxo HTTP de ponta a ponta.

**Exemplo:** um teste do OrdersService substitui ORDERS_REPOSITORY por uma implementação em memória para verificar regra e resultado. Um teste de integração do módulo confirma que o token está associado ao provider certo.

**Erro comum:** escrever mocks de cada método e chamar isso de validação da arquitetura, sem compilar o módulo real nem exercitar a conexão entre providers.

**Checagem:** o teste verifica a regra, a configuração do grafo ou a integração HTTP? Escolha evidência adequada à pergunta.

