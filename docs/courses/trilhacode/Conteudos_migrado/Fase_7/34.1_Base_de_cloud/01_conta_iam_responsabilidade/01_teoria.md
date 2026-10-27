---
arquivo_id: "f7-34-1-01-conta-iam-responsabilidade-01-teoria-md"
parent_key: "34.1"
tipo_arquivo: "theory"
assunto: "01_conta_iam_responsabilidade"
ordem: 1
itens_origem: ["### Microtópico 1 — Conta, regiões e responsabilidade compartilhada"]
---

### Microtópico 1 — Conta, regiões e responsabilidade compartilhada

Uma conta AWS é um limite administrativo e de faturamento. A maioria dos recursos é criada numa **região**; dentro dela, muitas cargas usam uma ou mais **zonas de disponibilidade** para separar falhas. O nome de um serviço não diz se o recurso é regional ou global: confirme o escopo antes de planejar redundância, custo e política de acesso. Recursos em regiões diferentes podem gerar tráfego e cobrança separados.

A segurança na nuvem é uma responsabilidade compartilhada. A AWS protege a infraestrutura física e a infraestrutura da nuvem; quem usa a conta continua responsável por dados, identidades, permissões, configuração de rede e segurança da aplicação. A parte operada pelo provedor muda conforme o serviço: com EC2, a pessoa cliente administra sistema operacional e software convidado; com RDS, a AWS opera mais componentes do serviço de banco, mas cliente ainda configura acesso, dados, credenciais, backups/retention e parâmetros sob sua responsabilidade. Serviço gerenciado reduz trabalho operacional, não elimina decisões de segurança.

Antes de provisionar, escolha a conta e região autorizadas para o exercício, identifique quem pode criar/apagar recursos e confirme limites da conta. Não use credenciais root no trabalho diário. Para pessoas, use identidades individuais e MFA; para aplicações em serviços AWS, prefira roles e credenciais temporárias a access keys estáticas. Uma **identity policy** concede ações sobre recursos; uma **trust policy** define quem pode assumir uma role. Menor privilégio e revisão de ambas limitam impacto de erro ou exposição.

