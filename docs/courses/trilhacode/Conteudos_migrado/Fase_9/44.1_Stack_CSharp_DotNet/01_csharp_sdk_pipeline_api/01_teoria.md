---
arquivo_id: "f9-44-1-01-csharp-sdk-pipeline-api-01-teoria"
parent_key: "44.1"
tipo_arquivo: "theory"
assunto: "01_csharp_sdk_pipeline_api"
ordem: 1
itens_origem: ["### 1. C#, SDK e pipeline de API"]
---


### 1. C#, SDK e pipeline de API
C# é uma linguagem tipada executada no ecossistema .NET. O .NET SDK fornece comandos e ferramentas para criar, compilar, executar e publicar projetos; NuGet distribui e restaura pacotes. Leia o `.csproj`, `global.json` quando existir e as dependências do projeto para identificar target framework, SDK esperado e bibliotecas.

ASP.NET Core processa requisições por um pipeline configurado no ponto de entrada, geralmente `Program.cs`. Middleware envolve a requisição e resposta; endpoints podem ser declarados como **Minimal APIs** ou por **controllers**. Minimal APIs reduzem cerimônia em endpoints diretos; controllers dão organização e convenções familiares quando há muitas ações, validação e filtros. Ambos podem compor a mesma aplicação, e nenhum estilo é automaticamente mais adequado para todo caso.

Um percurso de leitura comum: rota/endpoint → middleware/autenticação → handler/controller → serviço de domínio injetado → persistência → resposta. Compare responsabilidades com rotas, middleware, handlers e módulos em Node, mas confira a configuração explícita do projeto .NET.

