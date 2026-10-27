---
arquivo_id: "f3-8-3-03-checagem-emissao-diagnosticos-01-teoria"
parent_key: "8.3"
tipo_arquivo: "theory"
assunto: "03_checagem_emissao_diagnosticos"
ordem: 3
itens_origem: ["3. Checagem, emissão e diagnósticos"]
---

### 3. Checagem, emissão e diagnósticos
O compilador pode verificar tipos e emitir JavaScript. noEmit desativa a emissão quando outra ferramenta, como um bundler, gera os arquivos finais. noEmitOnError controla se a emissão para quando a checagem encontra erros. Confira o script de build do projeto para saber qual fluxo está em uso.

Leia nos diagnósticos a mensagem, o arquivo, a linha e o tipo esperado/recebido. Resolva a causa no contrato ou no fluxo; não acrescente any ou asserções só para silenciar o erro. Uma checagem limpa significa que as regras configuradas passaram nos arquivos incluídos. Não prova que todos os arquivos relevantes entraram na checagem, que a aplicação funciona em runtime ou que dados externos são válidos.

**Erro comum:** declarar “sem erros” sem confirmar o comando, os arquivos incluídos e se a build real foi executada.

