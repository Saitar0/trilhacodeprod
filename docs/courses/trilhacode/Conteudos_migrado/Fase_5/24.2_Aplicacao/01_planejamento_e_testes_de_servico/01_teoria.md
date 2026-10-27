---
arquivo_id: "f5-24-2-01-planejamento-e-testes-de-servico-01-teoria"
parent_key: "24.2"
tipo_arquivo: "theory"
assunto: "01_planejamento_e_testes_de_servico"
ordem: 1
itens_origem: ["theory-container", "Microtópico 1 — Planeje a evidência antes de abrir o editor", "Microtópico 2 — Teste o serviço com um dublê controlado"]
---

## Teoria

## Microtópico 1 — Planeje a evidência antes de abrir o editor

Use um fluxo concreto de criação de pedido. Ele recebe uma requisição, valida entrada, verifica uma regra, grava o pedido e responde ao cliente. Primeiro converta requisitos em comportamentos observáveis: pedido válido é persistido uma vez; entrada inválida não é persistida; duplicidade respeita a constraint do banco; rota retorna status e corpo previstos; falha relevante não deixa estado parcial.

Distribua perguntas pelo menor escopo que consegue respondê-las:
- **Serviço:** a regra produz o resultado correto e reage a uma falha de dependência? Substitua só a fronteira que não é o objeto da pergunta.
- **HTTP/módulo:** rota, pipe, guard, mapeamento de erro e serialização foram compostos corretamente? Suba a aplicação de teste; decida se o provider do banco será real ou substituído conforme a evidência.
- **Banco:** migrations, SQL/ORM, constraint, transação e leitura persistida funcionam juntos? Use o banco real de teste.
- **Fluxo amplo:** um cliente consegue completar uma operação representativa pela entrada pública? Inclua poucos E2E com cenário isolado.

Um teste pode cobrir mais de uma fronteira. Descreva exatamente quais componentes são reais e quais são substituídos; a palavra “integração” sozinha não revela o que ficou comprovado.

## Microtópico 2 — Teste o serviço com um dublê controlado

Para uma regra que não depende da semântica do banco, instancie o serviço ou monte o módulo Nest com uma implementação dublê do repositório. Controle o retorno e a falha do dublê. Verifique o resultado de negócio e, quando parte do contrato, a ação solicitada à dependência.

Exemplo de perguntas úteis:
- Com os campos válidos, o serviço solicita salvar os dados normalizados?
- Se a regra rejeita limite excedido, o repositório não recebe uma gravação?
- Se persistir falha, o serviço propaga ou traduz a falha conforme o contrato?

Esses testes são rápidos e localizam erro de regra, mas um repositório falso que sempre aceita dados não valida SQL, migrations, constraints ou comportamento transacional. Evite tornar o teste uma cópia da implementação: verifique o resultado e efeitos importantes, sem afirmar toda chamada interna na ordem exata quando isso não for requisito.

