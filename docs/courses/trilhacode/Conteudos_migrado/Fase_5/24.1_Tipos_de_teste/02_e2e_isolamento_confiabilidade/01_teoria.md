---
arquivo_id: "f5-24-1-02-e2e-isolamento-confiabilidade-01-teoria"
parent_key: "24.1"
tipo_arquivo: "theory"
assunto: "02_e2e_isolamento_confiabilidade"
ordem: 2
itens_origem: ["Microtópico 4 — E2E, dados isolados e confiabilidade"]
---

## Microtópico 4 — E2E, dados isolados e confiabilidade

Um E2E verifica um caminho de valor para o usuário ou consumidor, como criar um pedido por HTTP e observar o estado/resposta. Ele ajuda a detectar problemas de composição, rota, validação, serialização e configuração que testes isolados não veem. Por ter mais componentes e preparação, costuma ser mais lento e ter mais pontos de falha; mantenha os fluxos representativos, não cada combinação possível.

Cada teste deve poder rodar sozinho, em qualquer ordem e, quando aplicável, em paralelo. Prepare dados próprios, use identificadores únicos ou uma transação/namespace isolado, e limpe o que criou. Não dependa do estado deixado por outro teste. Em integração, uma base descartável ou esquema isolado ajuda a evitar dados residuais.

Testes instáveis ou flaky passam e falham sem mudança relevante no código. Causas frequentes incluem espera fixa de tempo, dependência de rede real, relógio não controlado, ordem de execução, concorrência por dados ou processo que não foi encerrado. Espere uma condição observável em vez de “dormir” por tempo arbitrário, controle a fonte não determinística e mantenha a falha reproduzível.

