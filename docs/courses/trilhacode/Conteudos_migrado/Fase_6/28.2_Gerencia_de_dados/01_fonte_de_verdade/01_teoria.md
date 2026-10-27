---
arquivo_id: "f6-28-2-01-fonte-de-verdade-01-teoria-md"
parent_key: "28.2"
tipo_arquivo: "theory"
assunto: "01_fonte_de_verdade"
ordem: 1
itens_origem: ["## Microtópico 1 — Classifique a origem e a fonte de verdade"]
---

## Microtópico 1 — Classifique a origem e a fonte de verdade
Antes de escolher onde guardar um valor, descubra quem o cria e quem pode alterá-lo. Estado **local de interface** atende uma interação limitada, como um modal aberto ou um rascunho de campo. Estado **compartilhado no cliente** atravessa componentes ou telas, como uma preferência de visualização. Dados **remotos** vêm de uma API e podem ser alterados por outras pessoas ou processos; o servidor é a fonte autoritativa.

Uma tela pode manter uma representação derivada para desenhar ou editar, mas deve saber de onde ela veio e como será reconciliada. Por exemplo, um formulário pode manter um rascunho local enquanto a pessoa digita e enviar uma mutação ao servidor ao salvar. Isso não transforma o rascunho na fonte autoritativa do perfil. Copiar toda resposta da API para uma store global cria duas versões potencialmente divergentes e exige que a aplicação sincronize ambas.

| Exemplo | Origem/fonte autoritativa | Estado adequado para começar |
| --- | --- | --- |
| Modal de confirmação aberto | Interface atual | Estado local do componente |
| Preferência de layout compartilhada entre telas | Escolha do usuário no cliente | Store de cliente ou preferência persistida, conforme o requisito |
| Lista de pedidos | API/servidor | Cache de consultas remotas |
| Texto ainda não salvo em um formulário | Edição atual da pessoa | Rascunho local, enviado como mutação |
| Página e filtro que devem ser compartilhados por link | URL | Parâmetros da URL e consulta remota derivada deles |

Persistir também é uma decisão de produto: sobreviver a navegação, fechar e abrir a aba, ou compartilhar por link são requisitos diferentes. Não persista dados por padrão sem avaliar privacidade, expiração e comportamento de logout.

