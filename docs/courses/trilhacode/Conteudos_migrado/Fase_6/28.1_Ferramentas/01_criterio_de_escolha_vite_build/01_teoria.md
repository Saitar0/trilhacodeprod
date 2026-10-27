---
arquivo_id: "f6-28-1-01-criterio-de-escolha-vite-build-01-teoria-md"
parent_key: "28.1"
tipo_arquivo: "theory"
assunto: "01_criterio_de_escolha_vite_build"
ordem: 1
itens_origem: ["## Microtópico 1 — Identifique o problema antes da ferramenta", "## Microtópico 2 — Use Vite para desenvolvimento e build"]
---

## Microtópico 1 — Identifique o problema antes da ferramenta
Comece descrevendo o problema em termos observáveis: iniciar o projeto localmente, gerar arquivos para publicação, compartilhar uma preferência entre telas ou buscar e manter atualizada uma resposta da API. Uma ferramenta é adequada quando resolve esse problema com menos custo e complexidade do que as alternativas já disponíveis.

Não confunda “estado” como uma categoria única. Uma variável temporária de formulário, a preferência de tema escolhida pela pessoa e os dados de uma consulta ao servidor têm ciclos de vida diferentes. Antes de adicionar uma biblioteca, pergunte onde o dado nasce, quem é responsável por atualizá-lo, quanto tempo deve viver e quais componentes precisam observá-lo. Estado local do React pode ser suficiente para uma interação confinada a um componente.

## Microtópico 2 — Use Vite para desenvolvimento e build
Vite fornece o servidor de desenvolvimento e a etapa de build para aplicações web. O servidor ajuda a desenvolver e verificar mudanças; o comando de build gera os artefatos que podem ser publicados em uma hospedagem compatível. Isso não transforma Vite em servidor de produção da aplicação nem em gerenciador de estado.

Os scripts do `package.json` documentam as tarefas disponíveis, como iniciar o servidor e gerar o build. Variáveis de ambiente exigem atenção: valores com prefixo `VITE_` são disponibilizados no código do cliente e entram no bundle durante o build. Portanto, não coloque senhas, tokens privados ou credenciais de banco nessas variáveis. Um valor que precisa permanecer secreto deve ser mantido em um servidor ou serviço seguro, fora do bundle público. Variáveis expostas também são strings e podem precisar de conversão e validação.

O resultado da build precisa ser servido por uma hospedagem configurada para a aplicação. O destino e as regras de fallback para rotas dependem da plataforma de publicação; “o build terminou” não prova por si só que todas as rotas funcionarão em produção.

