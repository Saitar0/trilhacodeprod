---
arquivo_id: "f5-19-2-03-fronteira-seguranca-contrato-01-teoria"
parent_key: "19.2"
tipo_arquivo: "theory"
assunto: "03_fronteira_seguranca_contrato"
ordem: 3
itens_origem: ["Microtópico 4 — Mantenha fronteira, segurança e contrato"]
---

## Microtópico 4 — Mantenha fronteira, segurança e contrato
Concentre o acesso a dados em uma fronteira compreensível, como repositório ou módulo de persistência, sem esconder do restante do time as decisões importantes. Documente a razão para uma exceção ao caminho usual, a forma de executar a consulta, suas premissas e como detectar regressões. Use testes para confirmar resultados, cardinalidade importante e comportamento transacional; use medições para avaliar desempenho.

SQL explícito também precisa de parâmetros vinculados para valores externos. Não concatene entradas não confiáveis. Se uma ordenação ou identificador for dinâmico, valide-o por uma lista permitida, já que parâmetros de consulta representam valores, não nomes de coluna. Preserve constraints e migrations no banco, mesmo quando a aplicação valida os mesmos dados.

**Exemplo:** um módulo de relatórios expõe uma função com nome e retorno definidos, executa SQL parametrizado e tem teste para o caso sem resultados, o caso típico e um volume maior. A justificativa informa qual necessidade específica levou ao SQL.

**Erro comum:** chamar a consulta bruta diretamente de vários pontos da aplicação ou deixar sua assinatura sem contrato. Isso espalha conhecimento de persistência e torna mudanças mais arriscadas.

**Checagem:** outra pessoa consegue entender por que a exceção existe, testar seu resultado e alterar o banco sem procurar SQL escondido em vários módulos?

