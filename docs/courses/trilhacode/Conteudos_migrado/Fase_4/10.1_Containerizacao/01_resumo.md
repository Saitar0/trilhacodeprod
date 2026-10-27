---
arquivo_id: "f4-10-1-01-resumo"
parent_key: "10.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Imagem é o artefato; container é uma instância que executa processos com configuração própria.
- Build depende de um contexto; Dockerfile e .dockerignore controlam o que entra na imagem.
- A camada gravável do container não substitui volume persistente.
- Publicar uma porta conecta o host ao container; uma rede de usuário conecta containers pelo nome.
- Volume não é backup, e versão/caminho de dados precisam corresponder à imagem usada.

