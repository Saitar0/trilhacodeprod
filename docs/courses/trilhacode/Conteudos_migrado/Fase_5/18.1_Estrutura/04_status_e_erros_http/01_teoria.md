---
arquivo_id: "f5-18-1-04-status-e-erros-http-01-teoria"
parent_key: "18.1"
tipo_arquivo: "theory"
assunto: "04_status_e_erros_http"
ordem: 4
itens_origem: ["5. Status e formato de resposta"]
---

### 5. Status e formato de resposta
Use códigos coerentes com o resultado. 200 representa sucesso com resposta; 201 indica criação bem-sucedida, podendo apontar o recurso criado; 204 representa sucesso sem conteúdo. 400 sinaliza requisição inválida; 401, falta de autenticação válida; 403, identidade sem permissão; 404, recurso não encontrado ou ocultado segundo política; 409, conflito com o estado atual. O status exato pode depender do contrato e da política de segurança; mantenha consistência e documente as decisões. [MDN — status HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status).

Defina um formato estável para erros, por exemplo um código legível, mensagem segura e lista opcional de campos inválidos. Não envie stack trace, consultas, caminhos internos, tokens ou detalhes de infraestrutura na resposta. Centralize a conversão de erros conhecidos para respostas HTTP e registre a falha inesperada no canal de diagnóstico adequado.

