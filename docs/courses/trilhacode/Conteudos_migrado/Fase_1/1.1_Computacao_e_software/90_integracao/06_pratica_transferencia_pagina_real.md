---
arquivo_id: "f1-1-1-90-integracao-06-pratica-transferencia-pagina-real"
parent_key: "1.1"
tipo_arquivo: "practice"
ordem: 3
itens_origem: ["P3"]
---

### 3. Transferência — desenhe o caminho de uma página real

Escolha uma página que você usa e represente o que acontece quando você a abre. Inclua cliente/navegador, DNS, servidor, requisição, resposta, frontend, backend e banco de dados quando fizerem parte do fluxo.

Use setas nomeadas. Não desenhe o banco como etapa obrigatória: marque-o como “consultado, se necessário”. Depois, escreva de cinco a oito frases explicando o fluxo e identifique pelo menos uma simplificação do desenho.

**Exemplo de esqueleto:**

```text
Pessoa → navegador (cliente)
       → consulta DNS para o domínio (se necessário)
       → requisição HTTP ao servidor
       → backend (se a aplicação precisar processar a solicitação)
       → banco de dados (se precisar consultar ou salvar dados)
       ← resposta HTTP
       ← navegador interpreta os recursos e apresenta a página
```

