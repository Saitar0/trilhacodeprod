---
arquivo_id: "f2-4-1-01-estrutura-html-aninhamento-validacao-01-teoria"
parent_key: "4.1"
tipo_arquivo: "theory"
assunto: "01_estrutura_html_aninhamento_validacao"
ordem: 1
itens_origem: ["HTML descreve estrutura e significado", "Aninhar e validar o documento"]
---

## Teoria

### HTML descreve estrutura e significado
HTML (HyperText Markup Language) é uma linguagem de marcação que organiza o conteúdo de uma página. Um elemento costuma ser escrito com uma tag inicial, conteúdo e tag final; elementos vazios, como `img` e `meta`, não envolvem conteúdo da mesma forma. Atributos acrescentam informações ao elemento, como `href` em links e `src` em imagens.

Um documento começa com `<!doctype html>`, seguido de `<html lang="pt-BR">`. O `<head>` contém metadados, título da aba e ligações a recursos; o `<body>` contém conteúdo apresentado na página. Use títulos em ordem lógica, parágrafos para texto, listas para conjuntos relacionados e links para destinos navegáveis.

```html
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Portfólio de Ana</title>
  </head>
  <body>
    <h1>Ana Silva</h1>
    <p>Desenvolvedora em formação.</p>
    <a href="https://example.com">Meu perfil</a>
  </body>
</html>
```

### Aninhar e validar o documento
Elementos devem ser organizados de acordo com sua estrutura e fechados de forma coerente. Um parágrafo pode conter texto e links, mas não deve envolver uma lista ou uma tabela. Feche o elemento dentro do qual começou antes de fechar o elemento externo. A identação ajuda a enxergar essa hierarquia, embora não altere por si só a estrutura interpretada pelo navegador.

Um validador HTML aponta problemas de sintaxe e conformidade que podem passar despercebidos. Corrija erros, examine avisos e teste o resultado no navegador. Validação não garante que o conteúdo esteja claro, que links e imagens carreguem ou que a página seja acessível; essas verificações exigem revisão própria.

