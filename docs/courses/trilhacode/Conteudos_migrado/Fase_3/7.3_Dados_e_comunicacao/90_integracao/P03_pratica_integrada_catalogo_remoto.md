---
arquivo_id: "f3-7-3-90-integracao-p03-pratica-integrada-catalogo-remoto"
parent_key: "7.3"
tipo_arquivo: "practice"
assuntos: ["01_formato_e_contrato_json", "02_requisicao_async_resposta_erros"]
ordem: 3
itens_origem: ["P3"]
---

### 3. Integrada — catálogo remoto com estados de interface
Consuma uma API de demonstração apropriada e apresente uma lista de itens. A interface deve mostrar carregamento, sucesso com itens, resultado vazio quando permitido e mensagens de falha. Inclua uma busca local ou filtro. Registre método, URL, status (quando houver resposta) e headers relevantes para depuração; não registre tokens nem dados pessoais.

Classifique os erros de rede, HTTP não bem-sucedido, parsing e formato inesperado separadamente. Garanta que o indicador de carregamento seja removido em qualquer resultado. Mostre conteúdo externo como texto e explique o que CORS protege, como reconhecer um possível bloqueio e por que a permissão precisa ser definida no servidor.

**Entregáveis:** código executável; instruções para configurar a URL da API e iniciar o projeto; tabela curta de estados e mensagens; nota descrevendo um cenário de falha testado.

**Dicas:** reutilize `carregarCatalogo`; coloque a mudança do indicador de carregamento num `finally`; não conclua que todo erro sem status é CORS — consulte console e aba de rede para investigar.

