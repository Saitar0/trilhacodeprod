---
arquivo_id: "f6-29-2-01-fronteiras-e-mocks-de-rede-p01-pratica-md"
parent_key: "29.2"
tipo_arquivo: "practice"
assunto: "01_fronteiras_e_mocks_de_rede"
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Teste o contrato HTTP do cliente com MSW
**Objetivo:** exercitar a chamada real do frontend e comprovar estados da lista por respostas controladas.

**Passos:**
1. Escolha uma tela que busque registros por HTTP e identifique método, endpoint, parâmetros e formato esperado da resposta.
2. Configure handlers MSW para sucesso com dados e coleção vazia, além de falha de autenticação ou servidor.
3. Renderize a tela e deixe que o código de produção faça a requisição; não substitua diretamente a função de API que o teste pretende verificar.
4. Para cada cenário, confira o resultado acessível no DOM e, quando relevante, os parâmetros e método recebidos pelo handler.
5. Restaure handlers entre os testes e configure a suíte para detectar requisições sem handler ou tentativas de acesso externo não planejadas.

**Dica:** reaproveite o handler padrão e faça override pontual para o cenário de erro ou vazio; documente que respostas mockadas não provam o serviço real.

**Entrega:** testes de integração para sucesso, vazio e falha, com um registro breve da fronteira coberta.

**Critérios de conclusão:** cliente e componente executam de verdade; respostas seguem o contrato declarado; cenários são determinísticos e não dependem de serviço externo.

