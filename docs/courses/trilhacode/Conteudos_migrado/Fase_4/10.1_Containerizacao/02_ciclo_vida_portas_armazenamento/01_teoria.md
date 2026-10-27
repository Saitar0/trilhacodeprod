---
arquivo_id: "f4-10-1-02-ciclo-vida-portas-armazenamento-01-teoria"
parent_key: "10.1"
tipo_arquivo: "theory"
assunto: "02_ciclo_vida_portas_armazenamento"
ordem: 2
itens_origem: ["3. Execute e inspecione o ciclo de vida", "4. Publique portas e escolha armazenamento"]
---

### 3. Execute e inspecione o ciclo de vida
`docker build -t consulta:dev .` constrói uma imagem com nome e tag. `docker run` cria e inicia um container. `docker ps` lista os ativos; `docker ps -a` inclui os parados; `docker logs` mostra a saída; `docker inspect` revela configuração; `docker stop` encerra; `docker rm` remove o container. A imagem continua existindo até ser removida separadamente.

Um container normalmente executa um processo principal. Se esse processo termina, o container deixa de estar em execução. Para observar o resultado, diferencie saída do processo, estado atual do container e existência da imagem. Opções como `--rm` removem o container ao terminar, mas não removem automaticamente a imagem nem volumes nomeados.

**Erro comum:** confundir um container parado com uma imagem removida ou com dados apagados.

### 4. Publique portas e escolha armazenamento
Portas internas não ficam automaticamente acessíveis no host. `-p 127.0.0.1:5432:5432` publica a porta 5432 do container apenas na interface local do host; `-p 5432:5432` costuma publicar em todas as interfaces do host, conforme o ambiente. A instrução EXPOSE documenta uma porta pretendida, mas não publica a porta por si só.

Volumes nomeados persistem fora do ciclo de vida do container. Bind mounts conectam um caminho do host ao container e são úteis em desenvolvimento, mas dependem da estrutura e permissões locais. Remover o container não é o mesmo que remover o volume; apagar o volume pode destruir os dados. Persistência também não é backup: um backup precisa de cópia recuperável independente e processo de restauração.

Exemplo para PostgreSQL 18 ou superior na imagem oficial:

```sh
docker volume create estudo_pg
docker run -d --name estudo-db \
  -e POSTGRES_PASSWORD=local-only \
  -p 127.0.0.1:5432:5432 \
  -v estudo_pg:/var/lib/postgresql \
  postgres:18
```

A imagem oficial do PostgreSQL 18 mudou o ponto de montagem recomendado para `/var/lib/postgresql`; em versões 17 e anteriores, a documentação da imagem indica `/var/lib/postgresql/data`. Confira a documentação da tag usada antes de reutilizar o comando. `local-only` é uma senha descartável para estudo, não uma credencial para produção.

**Erro comum:** montar o volume no caminho errado para a versão da imagem ou presumir que um volume equivale a backup.

