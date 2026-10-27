---
arquivo_id: "f6-27-3-01-fronteira-contrato-validacao-runtime-01-teoria-md"
parent_key: "27.3"
tipo_arquivo: "theory"
assunto: "01_fronteira_contrato_validacao_runtime"
ordem: 1
itens_origem: ["### 1. Descrever a fronteira entre cliente e API", "### 2. Separar tipo estático de validação em runtime"]
---

### 1. Descrever a fronteira entre cliente e API
Um contrato de dados define quais operações existem, o que o cliente envia, o que recebe, quais campos são obrigatórios, que valores podem ser nulos e quais erros podem ocorrer. Também documenta parâmetros, paginação, formatos, autenticação e limites relevantes. Um exemplo de resposta é útil, mas sozinho não define se os campos são sempre presentes nem como o servidor responde a falhas.

OpenAPI descreve operações HTTP e seus esquemas em um formato legível por pessoas e ferramentas. Pode servir para gerar documentação, tipos ou clientes, mas a especificação precisa refletir o comportamento real do servidor. Defina uma fonte de verdade e um processo para revisar/versionar mudanças; compartilhar um tipo TypeScript não garante que o payload em rede esteja conforme.

Considere esta resposta de listagem:

```json
{
  "items": [{ "id": "t-17", "title": "Revisar contrato", "dueDate": null }],
  "page": 1,
  "pageSize": 20,
  "total": 1
}
```

O contrato deve dizer se `dueDate` pode ser `null`, se `items` pode estar vazio, quais limites aceitam `page` e `pageSize`, e o que acontece quando a página solicitada não existe.

### 2. Separar tipo estático de validação em runtime
TypeScript analisa o código durante compilação; ele não verifica automaticamente se o servidor remoto enviou os campos prometidos. `response.json()` deve ser tratado como dado externo. Uma afirmação como `await response.json() as Task` muda a interpretação do compilador, mas não examina o valor recebido.

Use `unknown` na fronteira. Valide tipo, campos e restrições com uma função de validação, schema runtime ou biblioteca escolhida; depois transforme o dado para um modelo de domínio/UI. Se inválido, devolva erro controlado, estado de indisponibilidade ou adaptação explicitamente documentada. Não deixe que payload malformado derrube a tela e não silencie a incerteza com `any` ou `as`.

Validação verifica forma e invariantes locais — por exemplo, `page` inteiro positivo e `title` string. Ela não substitui autorização, integridade do banco ou confirmação de que um dado é verdadeiro. Nunca registre payload sensível inteiro só para investigar erro; inclua contexto seguro, como rota, código de erro e identificador de correlação.

