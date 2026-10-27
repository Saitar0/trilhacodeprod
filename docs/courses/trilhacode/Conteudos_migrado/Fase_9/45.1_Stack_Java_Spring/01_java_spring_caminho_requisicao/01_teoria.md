---
arquivo_id: "f9-45-1-01-java-spring-caminho-requisicao-01-teoria"
parent_key: "45.1"
tipo_arquivo: "theory"
assunto: "01_java_spring_caminho_requisicao"
ordem: 1
itens_origem: ["### 1. Java, Spring e o caminho de uma requisição"]
---


### 1. Java, Spring e o caminho de uma requisição
Java é compilado para bytecode executado pela JVM. Maven e Gradle automatizam resolução de dependências, compilação, testes e empacotamento; o projeto registra qual ferramenta e versão usa para tornar o build reproduzível. O Java define a linguagem e a plataforma; Spring Framework oferece componentes para configuração, injeção de dependências e aplicações web; Spring Boot reúne convenções, starters e auto-configuração para iniciar uma aplicação Spring com menos configuração manual. Auto-configuração depende do que está presente no classpath e pode ser ajustada quando a convenção não serve.

Em um endpoint típico, o **controller** interpreta HTTP e valida a entrada de borda, o **service** coordena a regra de negócio e o **repository** acessa a persistência. A entidade ou modelo persistido não precisa ser o formato público da resposta. A injeção por construtor declara as dependências necessárias e facilita fornecer substitutos em testes. Ela não torna a regra de negócio correta por si só: essa regra ainda precisa ser observável e testada.

Ao ler código, percorra: rota e parâmetros → controller → service → repository → resultado e resposta HTTP. Identifique onde erros de domínio viram respostas, onde a transação começa e quais dependências o container cria. Em Node, compare o papel desses componentes com rota/controller, serviço e camada de dados; a comparação é de responsabilidades, não de equivalência obrigatória de frameworks.

