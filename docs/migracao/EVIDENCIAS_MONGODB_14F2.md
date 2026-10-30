# Evidências MongoDB — Etapa 14F.2

## Identidade e isolamento

| Propriedade | Valor observado |
| --- | --- |
| Binário | `C:\Program Files\MongoDB\Server\9.0\bin\mongod.exe` |
| Versão | MongoDB `9.0.2`, Windows x64 |
| Topologia | Replica set de um membro; primário gravável |
| Replica set | `rs14f2_f85d35f7538647afb729c99588333084` |
| PID | `14088` |
| Endereço | `127.0.0.1:54159` |
| Diretório de dados | `%TEMP%\TrilhaCode14F2_f85d35f7538647afb729c99588333084\db` |
| Autenticação | Ativa; keyfile aleatório com ACL restrita ao usuário da execução |
| URI de teste | `mongodb://<usuário temporário>@127.0.0.1:54159/admin?replicaSet=rs14f2_<id da execução>&authSource=admin` |
| Banco por teste | Nome curto único `ta14f2_<caso>_<sufixo>` |

O gate antecedeu qualquer comando Mongo: o PID foi encontrado no CIM, o caminho do executável e a linha de comando continham os argumentos esperados (`--replSet`, `--bind_ip 127.0.0.1`, porta, `--dbpath`, keyfile e `--auth`), e o listener da porta exclusiva pertencia ao mesmo PID. Após iniciar o replica set, `hello` confirmou o nome esperado, um único membro loopback e `isWritablePrimary=true`. `connectionStatus` confirmou o principal autenticado temporário.

Docker Engine estava inacessível. O MongoDB service que já existia no Windows ficou em execução, mas não foi consultado, conectado nem modificado. Nenhuma URI padrão, URI de ambiente preexistente, `localhost:27017` ou banco de identidade desconhecida foi utilizado.

## Comando e resultado

```text
py -3.13 -m pytest unit_tests/test_typed_activity_persistence_mongodb.py -vv --tb=short
5 passed in 2.73s
```

Resultados observados no servidor descartável:

- Persistência dos seis tipos de atividade e pares público/privado.
- Reexecução idêntica retornou sem duplicar a versão.
- Revisão com versão esperada avançou head; versão stale foi rejeitada.
- Seis índices reais consultados; cinco únicos, um de histórico não único.
- O servidor rejeitou duplicidade de `activity_ref` no índice único do head.
- Falha injetada após a escrita pública e falha antes da atualização do head terminaram em rollback conforme esperado.
- Uma transação real foi confirmada e, depois, o cliente recebeu erro marcado como confirmação desconhecida. Replay idêntico encontrou a versão persistida e não criou duplicatas.
- Duas criações idênticas concorrentes convergiram para `created` e `unchanged`.
- Duas revisões divergentes concorrentes sobre o mesmo head tiveram um vencedor e um conflito.
- O caso RBAC usou três credenciais de teste diferentes e validou as permissões no servidor.

## Limites de cada evidência

- A falha depois da primeira escrita foi injetada no wrapper do cliente dentro de uma transação Mongo real; o estado persistido foi conferido após o aborto.
- A falha antes do head update foi injetada no wrapper antes da chamada real; a versão anterior e o head persistido foram relidos.
- O caso de confirmação desconhecida simulou a perda da confirmação **após** uma transação real ter commitado. Isso prova reconciliação pelo hash após commit já persistido, mas não simula uma partição de rede durante o protocolo de commit.
- Concorrência foi criada com `asyncio.gather` em clientes assíncronos independentes contra o servidor; não é teste de failover nem de múltiplos hosts.
- RBAC foi validado com papéis de coleção no único servidor descartável. Não prova a política de roles de um cluster de produção, integração com segredos/usuários de implantação ou auditoria externa de privilégios.
- Nenhuma migração de banco foi executada; `ensure_indexes()` do repositório criou os índices somente nos bancos exclusivos do teste.

## Encerramento do ambiente

O cliente administrativo emitiu `shutdown` autenticado para o próprio processo. Depois, foram verificados o encerramento do PID e a ausência de listener na porta. Apenas o diretório cujo nome continha o ID desta execução foi removido, após conferir sua localização sob `%TEMP%` e sua correspondência com o metadata local. Nenhum contêiner, volume, serviço ou diretório preexistente foi limpo.

Não foram registrados senha, keyfile, URI autenticada completa, tokens ou respostas corretas.
