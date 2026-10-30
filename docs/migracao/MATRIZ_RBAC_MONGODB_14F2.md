# Matriz RBAC MongoDB — Etapa 14F.2

O teste de integração criou papéis e credenciais aleatórios na instância descartável. Todos os privilégios foram limitados ao banco temporário de um teste. Os nomes e segredos dos usuários não são registrados.

| Principal de teste | Recurso | Ações concedidas | Verificação | Resultado |
| --- | --- | --- | --- | --- |
| Público | `typed_activity_public_versions` no banco de teste | `find` | Encontrou a versão pública | Permitido |
| Público | `typed_activity_private_versions` no banco de teste | Nenhuma | Tentou `find` direto | Negado pelo servidor, código 13 |
| Público | `typed_activity_public_versions` no banco de teste | Nenhuma escrita | Tentou `insert` | Negado pelo servidor, código 13 |
| Editorial | Quatro coleções editoriais do banco de teste | `find`, `insert`, `update`, `createIndex` | Salvou um rascunho pelo repositório | Permitido |
| Editorial | Coleção privada do banco de teste | `find` limitado ao próprio banco | Necessário para verificar e reconciliar revisões imutáveis | Permitido dentro do escopo editorial |
| Interno | Coleções pública e privada do banco de teste | `find` | Leu uma versão privada | Permitido |

## Interpretação

- O principal público não recebeu papel amplo, credencial administrativa ou privilégio sobre a coleção privada. A negação veio do MongoDB, não de uma filtragem do renderer.
- A separação de dados é física em coleções `typed_activity_public_versions` e `typed_activity_private_versions`; a credencial pública não consegue consultar a segunda coleção diretamente.
- O repositório editorial precisa ler a coleção privada para validar o head corrente e encontrar conteúdo idêntico em um replay. Portanto, o principal editorial de teste recebe `find` nessa coleção, além das ações de edição, mas somente no banco isolado.
- O principal interno recebe leitura privada e pública, sem ações de escrita no papel definido.
- O teste provou negação direta de consulta privada e escrita para o principal público, além de gravação editorial e leitura interna. Não prova roles de implantação/produção, segregação de equipes ou restrições de rede.

## Escopo e limpeza

Usuários e papéis foram criados no servidor desta execução e removidos no teardown. Cada caso usou banco temporário exclusivo, descartado ao fim. A credencial root temporária serviu apenas para provisionar o replica set e criar/remover os principals; não foi usada como evidência de acesso público. Nenhuma credencial foi registrada neste arquivo.
