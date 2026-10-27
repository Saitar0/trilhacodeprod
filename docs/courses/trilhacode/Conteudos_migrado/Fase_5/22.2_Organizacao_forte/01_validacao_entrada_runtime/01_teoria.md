---
arquivo_id: "f5-22-2-01-validacao-entrada-runtime-01-teoria"
parent_key: "22.2"
tipo_arquivo: "theory"
assunto: "01_validacao_entrada_runtime"
ordem: 1
itens_origem: ["Microtópico 1 — DTO e contrato de entrada em runtime", "Microtópico 2 — Pipes validam e transformam argumentos"]
---

## Microtópico 1 — DTO e contrato de entrada em runtime
DTO define o formato de dados que atravessa uma fronteira da aplicação, como o corpo de uma requisição. Uma anotação TypeScript ajuda o editor e o compilador, mas não verifica sozinha um JSON recebido em runtime. Interfaces, aliases e tipos genéricos desaparecem da execução; portanto, uma abordagem de validação precisa de metadados ou de um schema que exista em runtime.

No Nest atual, há caminhos distintos: ValidationPipe com classes DTO e decorators de class-validator, e StandardSchemaValidationPipe com schemas compatíveis com Standard Schema, por exemplo construídos por bibliotecas como Zod. O primeiro usa a classe e seus metadados; o segundo recebe um schema e pode inferir o tipo TypeScript dele. Escolha um padrão compatível com o projeto e a versão do framework, sem declarar que apenas classes podem validar toda entrada Nest.

Separe DTO de entrada do modelo persistido e da resposta pública. A entrada define o que o cliente pode enviar; a regra de domínio decide se aquela combinação é válida para o caso de uso.

**Exemplo:** um DTO de criação aceita nome e descrição. O sistema valida tipo e tamanho antes de chamar o caso de uso; a regra ainda verifica se a operação é permitida naquele estado.

**Erro comum:** confiar em tipo TypeScript, cast ou anotação como validação de uma requisição externa.

**Checagem:** qual código em runtime rejeita um valor inválido antes que ele alcance a regra de aplicação?

## Microtópico 2 — Pipes validam e transformam argumentos
Pipes atuam nos argumentos de uma rota antes de o handler ser chamado. ValidationPipe pode validar DTOs de classe, transformar plain objects em instâncias e converter valores primitivos quando a opção correspondente está habilitada. A configuração whitelist remove propriedades que não têm decorators de validação; combiná-la com forbidNonWhitelisted rejeita propriedades extras. Essas opções são específicas desse caminho baseado em class-validator. Em schemas, a política de propriedades desconhecidas depende do próprio schema.

Validação e transformação devem ser explícitas. Parâmetros de caminho e query chegam como texto; converter texto para número não substitui verificar limites, formato ou existência do recurso. Validação estrutural de entrada também não substitui regra de negócio: “campo é uma data válida” e “pedido pode ser cancelado agora” são perguntas diferentes.

**Exemplo:** o pipe rejeita quantidade não numérica ou payload com campo administrativo inesperado; o caso de uso verifica se ainda há estoque para aquela quantidade.

**Erro comum:** acreditar que whitelist permite automaticamente todos os campos declarados no DTO. No caminho class-validator, os decorators fornecem metadados usados para reconhecer propriedades aceitas.

**Checagem:** qual camada responde por formato e tipo? Qual responde por invariantes e estado do domínio?

