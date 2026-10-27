---
arquivo_id: "f7-34-1-03-dns-tls-caminho-requisicao-01-teoria-md"
parent_key: "34.1"
tipo_arquivo: "theory"
assunto: "03_dns_tls_caminho_requisicao"
ordem: 3
itens_origem: ["### Microtópico 3 — Identidade e caminho da requisição"]
---

### Microtópico 3 — Identidade e caminho da requisição

Uma requisição de navegador a uma aplicação pode seguir este caminho: DNS encontra o destino do domínio; cliente negocia TLS/HTTPS; load balancer ou proxy recebe a conexão; a aplicação processa a rota; se necessário, ela acessa RDS pela rede privada. DNS traduz nomes e não autentica pessoas. TLS protege o tráfego no trecho em que está configurado; não prova que o usuário tem permissão para consultar o recurso. Se TLS termina no balanceador, avalie também como proteger o trecho balanceador→aplicação e aplicação→banco segundo o risco e suporte.

O load balancer distribui conexões para alvos registrados e pode verificar saúde desses alvos; não substitui a lógica de autorização da aplicação. Route 53 pode hospedar/resolver DNS; ACM pode provisionar e associar certificados conforme serviço/região e cenário suportados. Documente quem renova/associa o certificado e como domínio aponta ao endpoint. Para produção, pense em mais de uma zona, health checks, observabilidade e recuperação; o laboratório simples é apenas um recorte pedagógico.

S3 armazena objetos em buckets; não é um filesystem POSIX montado por padrão. Mantenha acesso público bloqueado quando não for requisito, conceda acesso por role/policy e não publique arquivos privados só para contornar configuração do site. Dados em objeto também exigem política de ciclo de vida, retenção, criptografia e acesso adequados ao caso.

