---
arquivo_id: "f1-1-1-90-integracao-03-pratica-independente-compare-fluxos"
parent_key: "1.1"
tipo_arquivo: "practice"
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — compare dois fluxos

Uma enciclopédia fictícia tem uma página pública `/sobre` e uma página `/minha-conta` que mostra o nome da pessoa autenticada. Represente os dois fluxos, da ação da pessoa até a tela atualizada.

**Entregue:**

1. Dois diagramas com participantes e setas nomeadas.
2. Uma indicação do que pode ser resolvido no frontend e do que exige processamento no backend.
3. Uma indicação explícita de onde o banco de dados pode ser consultado — e por que ele não é obrigatório no primeiro fluxo.
4. Uma frase dizendo quando o DNS entra no fluxo e por que não precisa aparecer como uma consulta nova em toda requisição.

**Dicas progressivas**

- Primeiro, escreva quem inicia a ação e quem recebe cada mensagem. Depois, nomeie a mensagem (por exemplo, requisição HTTP, consulta ao banco ou resposta HTTP).
- Na página pública, considere que o conteúdo pode estar no próprio servidor ou em cache. Na página da conta, considere que o servidor precisa verificar a sessão e obter dados autorizados. Não suponha que o navegador fale diretamente com o banco.

