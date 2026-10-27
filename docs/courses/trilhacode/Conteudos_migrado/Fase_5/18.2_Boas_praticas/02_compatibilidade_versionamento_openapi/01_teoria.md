---
arquivo_id: "f5-18-2-02-compatibilidade-versionamento-openapi-01-teoria"
parent_key: "18.2"
tipo_arquivo: "theory"
assunto: "02_compatibilidade_versionamento_openapi"
ordem: 2
itens_origem: ["2. Compatibilidade e versionamento", "3. OpenAPI como contrato legível por máquinas"]
---

### 2. Compatibilidade e versionamento
Uma API evolui como contrato entre servidor e consumidores. Mantenha compatibilidade quando possível e crie nova versão quando a alteração for incompatível e não puder ser migrada sem quebra. Versão no caminho, como /v1, é uma escolha explícita; cabeçalho ou parâmetro também são políticas possíveis. Não há necessidade de aumentar a versão para toda mudança.

Uma alteração aditiva pode parecer segura, mas ainda quebrar clientes com validação rígida ou enums exaustivos. Remover ou renomear campo, mudar significado, tornar obrigatório um campo antes opcional ou alterar status/resposta pode quebrar consumidores. Publique política de depreciação, período de suporte e instruções de migração. [Microsoft — design de APIs](https://learn.microsoft.com/en-us/azure/architecture/microservices/design/api-design).

### 3. OpenAPI como contrato legível por máquinas
OpenAPI descreve operações, parâmetros, autenticação, corpos, schemas e respostas HTTP de uma API. Essa descrição permite que pessoas e ferramentas conheçam o contrato; ferramentas podem gerar documentação, clientes, validações e testes. Documente sucesso e erros conhecidos, incluindo campos, tipos, obrigatoriedade, limites e exemplos. Para listas, descreva parâmetros de página, limite máximo, ordenação, campos de retorno e condição de fim.

A especificação não muda a implementação por conta própria. Mantenha documentação e servidor sincronizados com validação em runtime, testes de contrato ou uma abordagem de geração adotada pelo projeto. Uma descrição OpenAPI válida pode ainda estar desatualizada em relação ao comportamento real. [OpenAPI Specification](https://spec.openapis.org/oas/).

