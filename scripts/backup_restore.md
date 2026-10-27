# Backup e restauração do MongoDB

## Backup manual com mongodump

Instale/ use o MongoDB Database Tools em uma máquina administrativa confiável. Defina a URI por prompt ou secret manager (não salve credenciais no histórico do shell nem em arquivos versionados):

```bash
read -rsp 'MONGO_URL: ' MONGO_URL; export MONGO_URL; echo
export DB_NAME=trilhacode_production
mongodump --uri="$MONGO_URL" --db="$DB_NAME" --archive="trilhacode-$(date -u +%Y%m%dT%H%M%SZ).archive.gz" --gzip
unset MONGO_URL
```

O usuário Mongo precisa apenas de leitura (`read`) no banco de origem para gerar o dump. Guarde o arquivo criptografado e controle o acesso.

## Restaurar e testar em um banco temporário

Crie no MongoDB de teste um banco isolado, por exemplo `trilhacode_restore_check`, e use uma URI temporária. Não restaure diretamente em produção durante este teste.

```bash
read -rsp 'MONGO_URL de teste: ' RESTORE_MONGO_URL; export RESTORE_MONGO_URL; echo
mongorestore --uri="$RESTORE_MONGO_URL" --archive=trilhacode-backup.archive.gz --gzip \
  --nsFrom='trilhacode_production.*' --nsTo='trilhacode_restore_check.*' --drop
```

Valide contagens e documentos essenciais com `mongosh`, execute a aplicação apontando para o banco temporário e confirme `/health`, `/ready`, login e leitura de conteúdo. Registre data, backup usado e resultado. Ao terminar, remova o banco temporário conforme o procedimento operacional do provedor.

## Agendar no Coolify e enviar para S3

1. Na AWS, crie um bucket dedicado apenas aos backups Trilha Code, habilite bloqueio de acesso público e criptografia em repouso (SSE-S3 ou SSE-KMS). Se usar KMS, restrinja também a chave.
2. Crie um usuário/role IAM exclusivo para Coolify. Restrinja as ações necessárias de listagem/objetos ao ARN desse bucket e prefixo. Não conceda acesso a outros buckets. Guarde access key/secret no secret store do Coolify, nunca neste repositório.
3. No Coolify, abra **S3 Storages**, cadastre endpoint/região/bucket/prefixo e credenciais, e valide a conexão.
4. Abra o recurso MongoDB do ambiente correto > **Backups** > **Add**. Defina frequência (por exemplo, diário às 02:00 no timezone exibido), bancos a incluir, timeout adequado, e retenção local/S3 (por exemplo, 7 cópias e 30 dias; ajuste à política de recuperação).
5. Em **S3 storage**, selecione a conexão validada, habilite S3 e salve. Mantenha cópia local até validar a integração; apagar após upload é opcional. Configure retenção S3 explicitamente.
6. Clique **Back up now**. Na execução, confira status **Success**, banco esperado, arquivo com tamanho maior que zero e upload S3 bem-sucedido. Confirme também que o objeto apareceu no bucket/prefixo.
7. Faça periodicamente restore em banco descartável. Backup bem-sucedido sozinho não prova que a restauração funciona.

As opções e nomes de tela refletem o fluxo de backups de banco atual do Coolify; confirme na documentação oficial antes de mudanças operacionais: [Coolify Database Backups](https://coolify.io/docs/databases/backups). Um dump do banco da aplicação é diferente do backup interno da instância Coolify.
