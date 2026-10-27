---
arquivo_id: "f5-21-1-02-acoplamento-custo-mudanca-01-teoria"
parent_key: "21.1"
tipo_arquivo: "theory"
assunto: "02_acoplamento_custo_mudanca"
ordem: 2
itens_origem: ["Microtópico 2 — Acoplamento: dependências e custo de mudança"]
---

## Microtópico 2 — Acoplamento: dependências e custo de mudança
Acoplamento é a dependência entre partes do sistema. Uma dependência existe quando um módulo conhece ou precisa de outro para compilar, executar ou cumprir seu contrato. Acoplamento não é automaticamente ruim: colaboração entre partes é necessária. O problema aparece quando um detalhe muda em um módulo e força mudanças espalhadas, dificulta entender a regra ou impede substituir/testar uma dependência relevante.

Desenhe a direção das dependências e pergunte que conhecimento atravessa a fronteira. Um módulo de regra que depende diretamente de detalhes de HTTP, banco ou SDK de fornecedor costuma ficar mais difícil de reutilizar ou testar isoladamente. Entretanto, introduzir interfaces e camadas também tem custo. A abstração deve proteger uma fronteira com variação ou custo real, não somente repetir os nomes das classes concretas em interfaces.

Uma fronteira pode ser uma função com parâmetros claros, um módulo, um adaptador, uma interface ou um contrato de serviço. Escolha o menor mecanismo que torne o comportamento e a mudança mais fáceis de compreender.

**Exemplo:** a regra de cálculo de frete chama diretamente um SDK do fornecedor e constrói a configuração internamente. Se trocar fornecedor é uma mudança plausível ou a chamada externa impede teste, um contrato de cotação com adaptador pode isolar esse detalhe.

**Erro comum:** criar interface para cada classe sem variação prevista, ou chamar tudo de altamente acoplado só porque duas funções colaboram.

**Checagem:** que alteração concreta fica mais localizada com a fronteira proposta? Nomeie a mudança e quais módulos deixam de precisar conhecer o detalhe.

