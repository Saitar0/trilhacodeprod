# Plano de recuperação do staging

**Estado verificado em 2026-10-18:** a API aparece `exited:unhealthy` sem container e sem histórico de deploy; não há logs de processo disponíveis para esse recurso parado. O MongoDB de staging está saudável, privado e usa volumes persistentes, mas não há backup agendado listado nem evidência de restore. O Coolify não mostra uma imagem imutável configurada para a API. A causa raiz exata da indisponibilidade permanece indeterminada com os dados disponíveis.

## Identidade e backup observados

- Banco Coolify `trilhacode-staging-mongodb`, UUID de recurso `3jo4k9aes1iqn4qlqqeyyh4y`, servidor Coolify `localhost`, MongoDB standalone 7, banco inicial `trilhacode_staging`, sem porta publicada e `running:healthy`. Esse UUID identifica o recurso Coolify, **não** o container Docker.
- Volumes persistentes Coolify: `/data/configdb` usa `3jo4k9aes1iqn4qlqqeyyh4y-mongodb-configdb-n3ry5kmbvok7btuv9nebymsr` (storage UUID `mbic79qapkm95aiwdythvzjg`); `/data/db` usa `3jo4k9aes1iqn4qlqqeyyh4y-mongodb-db-n3ry5kmbvok7btuv9nebymsr` (storage UUID `hi6bplsj8ibyjofxflaa1vgc`). Os mounts preservam dados em disco, mas não são cópia de segurança.
- A consulta de agendas retornou zero backups; não há execuções de backup nem prova de restauração. O canal Coolify disponível permite leitura, mas não expõe uma operação autorizada para criar agendas ou backups.
- O ID Docker completo, nome Docker, redes e aliases do Mongo não são fornecidos pela metadata consultada. Não os deduza dos UUIDs do Coolify nem de nomes presumidos.
- Aplicação Coolify `trilhacode-staging-api`, UUID `skmrkg3jb1ifhx0qwwneeirx`, tem domínios `api.staging.saitaro.tech` e `www.api.staging.saitaro.tech`, Dockerfile `/backend/Dockerfile.prod`, porta 8000, sem container e sem imagem/tag de registry configuradas. O health check Coolify está desativado e seu caminho armazenado é `/`; o Dockerfile versionado tem `HEALTHCHECK` em `/health`. Configure o check Coolify para `/health` quando a aplicação for recuperada, mas isso sozinho não explica a ausência do container.
- O recurso API Coolify aponta para a branch `main`, enquanto o procedimento versionado de staging e o job `deploy-staging` esperam a branch `staging`. Essa divergência operacional precisa ser resolvida e confirmada pelo operador antes de qualquer webhook/deploy. O recurso também guarda Compose path `/docker-compose.yaml`, diferente do `compose.yaml` versionado; como o build pack é Dockerfile, não está provado se esse campo participa do build.

MongoDB standalone não oferece `--oplog` para transformar um `mongodump` online em snapshot de ponto no tempo. Antes de aceitar um dump como backup consistente, identifique e pause com segurança todos os escritores durante toda a captura, ou use um snapshot de volume com procedimento MongoDB apropriado que controle as gravações e inclua os arquivos de dados e journal. A API estar parada não prova que não existam outros escritores. Faça a cópia cifrada em armazenamento durável fora do host/volume, aplique retenção explícita (meta inicial: 7 cópias diárias e 30 dias fora do host), registre tamanho/hash e teste `mongorestore` em Mongo 7 descartável sem rota para staging/produção. Verifique bancos/coleções e leitura de documentos sintéticos ou sanitizados sem colocar dados pessoais em logs. A política de retenção e o destino externo precisam ser confirmados no provedor antes da configuração; não crie nem altere recursos de armazenamento nesta etapa.

O plano abaixo não autoriza deploy, restart, migração, criação de índice, alteração de banco ou mudança de rede. Preserve a aplicação e o Mongo existentes; não recrie o projeto inteiro nem execute comandos Docker globais.

## Bloqueios antes da recuperação

1. Identifique no Coolify o projeto, servidor e recurso de API de staging pelo nome e UUID. Pare se o alvo não for inequivocamente Trilha Code. Não selecione recursos por nomes genéricos como `mongo` ou `api`.
2. Configure e execute um backup consistente do Mongo de staging em armazenamento durável fora do container, após provar que os escritores podem ser pausados sem atingir serviços compartilhados. Registre horário, retenção e identificador. Restaure uma cópia em Mongo descartável isolado, sem conexão à rede de produção, e valide que ela abre e contém o banco esperado. O diretório de dados persistente não substitui backup.
3. Confirme com consultas somente leitura o nome do banco, host interno, versão do Mongo, versão do schema e índices. Use a credencial de aplicação só para o preflight necessário; a credencial do G2 deve ser read-only. Não rode `migrate`, `ensure-indexes`, `seed` nem `resume-restores` se a versão, duplicatas ou configuração divergirem.
4. Construa a imagem a partir de um commit imutável aprovado, confirme origem e digest e teste `/health` e `/ready` em ambiente descartável. A configuração atual aponta para a branch `main` com `HEAD`; isso não identifica o commit de um container que não existe.
5. Compare as configurações do Coolify com o repositório: build pack Dockerfile, contexto na raiz, `backend/Dockerfile.prod`, porta `8000`. O campo Compose aparece como `/docker-compose.yaml`, enquanto o repositório usa `compose.yaml`; confirme se o campo é ignorado pelo build pack Dockerfile ou corrija a referência no recurso antes do build. O health check está desativado e o caminho cadastrado `/` não é a rota de health da API; configure `/health` e confirme também `/ready`.
6. Verifique a URI de conexão apenas pelo gerenciador de segredos, sem imprimir valores. Confirme `DB_NAME=trilhacode_staging`, autenticação na base correta e resolução pelo hostname privado do Mongo existente. Não altere nem substitua os volumes.
7. Defina `TRUSTED_PROXY_IPS` com os endereços/CIDRs reais do proxy Coolify após confirmar a topologia. Não copie `127.0.0.1` do padrão da imagem para uma rede de containers sem comprovação.
8. Antes de validar entrega de e-mail em staging, configure SMTP real por segredo de runtime, remetente/domínio autorizado, TLS e envio de saída. O transporte local de preview grava mensagens em disco e não demonstra entrega a usuários.
9. Confirme o artefato e o domínio do frontend. A configuração de staging consultada lista uma aplicação de API e um Mongo; não há evidência de um frontend implantado no projeto.

## Provedor de e-mail transacional

Avaliação das páginas oficiais consultadas em 18/10/2026:

| Serviço | Plano de baixo volume | SMTP e configuração | Avaliação para Trilha Code |
| --- | --- | --- | --- |
| Resend | Gratuito: 3.000/mês, limitado a 100/dia; Pro: US$ 20/mês para 50.000, sem limite diário e US$ 0,90 por 1.000 excedentes | `smtp.resend.com:465` com TLS implícito; usuário `resend` e API key como senha. Requer verificar o domínio/remetente e publicar os registros DNS indicados | Recomendação inicial: menor atrito para staging e SMTP simples, com quota gratuita limitada para teste real. Avaliar Pro antes de ultrapassar 100 mensagens/dia. |
| Postmark | Developer: 100/mês; Basic: US$ 15/mês para 10.000, excedente US$ 1,80 por 1.000; Pro: US$ 16,50/mês e US$ 1,30 por 1.000 excedentes | SMTP transacional em `smtp.postmarkapp.com`, STARTTLS; token do servidor como usuário e senha (ou credenciais SMTP dedicadas). Sem limite diário indicado para planos pagos | Forte alternativa se entrega transacional e separação por streams forem prioridade; não há plano gratuito adequado a fluxo de staging contínuo. |
| Amazon SES | Essentials: US$ 0,16/1.000 até 10 milhões/mês. Pro: US$ 0,22/1.000 e US$ 105/mês por conta/região. Enterprise: US$ 0,23/1.000 e US$ 500/mês por conta/região | SMTP endpoint varia por região, TLS obrigatório e credenciais SMTP distintas das chaves AWS. Exige identidade de remetente verificada. Contas no sandbox ficam limitadas a 200 mensagens/24h, 1 por segundo e destinatários verificados | Menor custo por volume no Essentials, mas maior carga de configuração IAM/região e gate de saída do sandbox; escolher quando a operação AWS já estiver estabelecida. |

Fontes oficiais: [Resend pricing](https://resend.com/pricing?product=transactional), [Resend SMTP](https://resend.com/features/smtp-service), [Postmark pricing](https://www.postmarkapp.com/pricing), [Postmark SMTP](https://www.postmarkapp.com/developer/user-guide/send-email-with-smtp), [Amazon SES pricing](https://aws.amazon.com/ses/pricing/), [SES sandbox quotas](https://docs.aws.amazon.com/ses/latest/dg/manage-sending-quotas.html), [SES SMTP requirements](https://docs.aws.amazon.com/ses/latest/dg/send-email-smtp.html).

Nenhuma conta, domínio de envio, chave ou credencial SMTP está configurada ou acessível nesta sessão. Para habilitar entrega real, o responsável precisa escolher/criar a conta do provedor, verificar domínio sob controle da organização, configurar SPF/DKIM (e DMARC conforme política), selecionar remetente autorizado e fornecer os segredos SMTP somente no gerenciador do Coolify. Testar envio para caixa de controle, confirmação, uso único/expiração, recuperação e rejeição de falha SMTP, sem registrar token ou conteúdo pessoal. Até esse teste, SMTP de staging permanece não homologado.

Interrompa se backup/restore não for comprovado, alvo ou banco divergirem, não houver imagem identificada por digest, o preflight reportar conflitos/duplicatas/erro, a conexão apontar a outro serviço, SMTP falhar ou o health/readiness não ficar verde. Não contorne esses bloqueios com restart ou recriação do Mongo.

## Recuperação mínima, quando todos os bloqueios estiverem satisfeitos

1. Salve o estado de configuração atual e o commit/digest novo; confirme quem pode executar rollback.
2. Implante somente a API de staging a partir do digest aprovado no recurso de API existente, preservando o Mongo e seus volumes. Não dispare o workflow manual de publicação nem altere production.
3. Confirme container, imagem/digest, rede privada para Mongo, porta interna `8000`, health `/health`, readiness `/ready`, versão de schema, logs sanitizados e ausência de reinícios.
4. Faça smoke test autorizado: cadastro com caixa de teste, confirmação, login, rota de aluno, negação de conta não verificada, recuperação de senha e uma rota administrativa com usuário de teste. Verifique entrega e rejeição de replay dos tokens; remova os dados de teste pelo fluxo de limpeza aprovado.
5. Implante o frontend somente depois da API saudável; verifique domínio, CORS, cookies `Secure`, CSP e fluxo completo no navegador.

## Reversão

Antes de iniciar, registre um digest anterior comprovadamente saudável e o procedimento de rollback disponível no Coolify. Se não existir artefato anterior nem evidência de rollback, não comece a implantação. Em falha de código sem mudança de schema, reverta a API ao digest anterior e verifique health/readiness e login. Restaure o backup somente se houver perda ou corrupção de dados, mediante plano separado que considere gravações posteriores. Não remova container, volumes, rede ou banco como parte de rollback de rotina.

## Evidência pendente

- Logs do deploy/contêiner que expliquem o estado `exited:unhealthy`.
- Digest e commit realmente executados.
- Backup agendado, execução recente e restore isolado bem-sucedido.
- Compatibilidade de schema e índices no Mongo de staging.
- Credencial de aplicação e conectividade ao Mongo existentes.
- IPs da rede do proxy, SMTP transacional e frontend de staging.
- Digest anterior saudável e rollback testado.
