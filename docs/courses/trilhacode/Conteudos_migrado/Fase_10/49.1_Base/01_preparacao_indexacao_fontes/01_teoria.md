---
arquivo_id: "f10-49-1-t01"
parent_key: "49.1"
tipo_arquivo: "theory"
assunto: "01_preparacao_indexacao_fontes"
ordem: 1
itens_origem: ["### 1. Preparar e indexar fontes"]
---


### 1. Preparar e indexar fontes
RAG (retrieval-augmented generation) combina busca em uma coleção externa com geração de uma resposta condicionada aos trechos recuperados. A ingestão começa antes do modelo: confirme autorização e formato, limite tamanho, extraia texto, normalize o necessário e preserve origem, identificador, versão/data e permissões. Registre falhas de extração; um PDF escaneado sem OCR adequado, por exemplo, pode produzir um índice incompleto sem que a busca revele o motivo.

Divida o texto em chunks usando limites que preservem significado — títulos, seções ou janelas por tamanho — e guarde metadados que permitam reconstruir a localização e a versão original. Chunks curtos podem separar contexto necessário; chunks longos podem misturar assuntos e consumir mais contexto. Sobreposição pode preservar continuidade, mas também duplica conteúdo e custo. Não existe tamanho universal: compare estratégias no corpus e nas perguntas que importam. Mudanças de documento precisam atualizar ou remover os chunks correspondentes; mantenha versão do extrator, regra de chunking e modelo de embedding para reproduzir o índice.

