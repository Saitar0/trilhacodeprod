---
arquivo_id: "f10-48-1-t02"
parent_key: "48.1"
tipo_arquivo: "theory"
assunto: "02_fronteira_backend_contrato"
ordem: 2
itens_origem: ["### 2. Fronteira no backend e contrato da aplicação"]
---


### 2. Fronteira no backend e contrato da aplicação
A chamada autenticada deve ocorrer no servidor. Guarde a credencial em configuração protegida ou serviço de segredos; não a inclua no bundle do navegador, no repositório, em mensagem de erro ou em log. Defina qual entrada a aplicação aceita, tamanho máximo, resposta que precisa devolver e quais dados podem ser enviados ao provedor. Use dados sintéticos nos exercícios e verifique os termos/políticas aplicáveis antes de enviar dados reais.

Coloque o acesso externo atrás de uma fronteira pequena, por exemplo `gerarResposta(entrada, opções)`, com cliente e configuração injetáveis. A aplicação de domínio deve depender do seu contrato e não espalhar SDK, nomes de modelos e formatos de resposta por todas as camadas. Uma interface comum facilita testes e algumas trocas, mas não apaga diferenças entre provedores: streaming, saída estruturada, ferramentas, multimodalidade, limites e erros podem exigir capacidades específicas. Evite uma abstração que prometa portabilidade que o código não tem.

Estabeleça limites compatíveis com o fluxo: timeout, tamanho de entrada e saída, concorrência e tratamento de rate limit. Devolva estado de erro compreensível sem expor credencial nem conteúdo sensível. Um timeout não prova que o provedor não processou a solicitação; retries podem aumentar custo e, se houver ação externa, repetir efeitos. A política de repetição deve considerar o tipo de operação e a semântica do endpoint.

