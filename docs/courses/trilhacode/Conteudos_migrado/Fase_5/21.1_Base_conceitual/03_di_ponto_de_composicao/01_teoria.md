---
arquivo_id: "f5-21-1-03-di-ponto-de-composicao-01-teoria"
parent_key: "21.1"
tipo_arquivo: "theory"
assunto: "03_di_ponto_de_composicao"
ordem: 3
itens_origem: ["Microtópico 3 — Injeção de dependência e ponto de composição"]
---

## Microtópico 3 — Injeção de dependência e ponto de composição
Injeção de dependência (DI) é uma forma de fornecer colaboradores a um módulo em vez de fazê-lo localizar ou construir, por conta própria, dependências que não deveria controlar. Isso deixa explícito o que o módulo precisa e permite configurar implementações em um ponto de composição da aplicação. A configuração fica separada do uso.

Uma dependência pode ser fornecida por parâmetro de função, construtor, framework ou outro mecanismo simples. Interface formal é necessária quando ajuda a expressar contrato ou desacoplar uma variação real; funções e tipos existentes também podem servir. DI não significa que toda classe precisa de container, nem que toda implementação deve ser substituível em produção.

**Exemplo:** um caso de uso recebe um repositório no construtor. A inicialização da aplicação escolhe a implementação de banco; um teste pode fornecer uma implementação em memória se ela reproduz o comportamento relevante.

**Erro comum:** usar container, singleton ou localizador global para esconder dependências. O código parece simples na chamada, mas a lista de colaboradores e a configuração ficam difíceis de descobrir.

**Checagem:** lendo a assinatura do módulo, outra pessoa consegue identificar o que ele precisa para funcionar e de onde a aplicação fornece essas dependências?

