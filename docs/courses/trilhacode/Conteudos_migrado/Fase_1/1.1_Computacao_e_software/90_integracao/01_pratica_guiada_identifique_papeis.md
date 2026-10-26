---
arquivo_id: "f1-1-1-90-integracao-01-pratica-guiada-identifique-papeis"
parent_key: "1.1"
tipo_arquivo: "practice"
ordem: 1
itens_origem: ["P1"]
---

## Prática — três níveis

Faça as atividades em ordem. A primeira é guiada e trabalha a identificação dos papéis; a segunda pede que você modele dois fluxos; a terceira transfere o raciocínio para uma página real. Você pode desenhar à mão ou usar texto e setas.

### 1. Guiada — identifique os papéis

Para cada situação, indique o componente ou papel mais diretamente envolvido. Alguns fluxos envolvem mais de um componente. Responda também se há uma consulta a banco de dados necessariamente.

| Situação | O que identificar |
|---|---|
| A pessoa abre uma página digitando `loja.exemplo/produtos`. | Cliente, DNS e quem envia/recebe a requisição HTTP. |
| A pessoa abre um menu já carregado e a tela apenas mostra opções. | Onde a ação pode ser processada e se uma solicitação ao servidor é obrigatória. |
| A pessoa envia um formulário de login. | Qual parte recebe os dados, onde a regra de autenticação deve ser aplicada e como o resultado volta. |
| A aplicação precisa buscar o endereço de entrega salvo. | Qual componente deve solicitar os dados persistidos e qual componente os mantém. |
| O navegador precisa saber a que destino de rede corresponde `loja.exemplo`. | Para que serve o DNS e o que ele não fornece. |

