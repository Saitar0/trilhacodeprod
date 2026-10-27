---
arquivo_id: "f4-10-1-03-redes-de-containers-01-teoria"
parent_key: "10.1"
tipo_arquivo: "theory"
assunto: "03_redes_de_containers"
ordem: 3
itens_origem: ["5. Conecte containers por uma rede"]
---

### 5. Conecte containers por uma rede
Uma rede bridge criada pelo usuário permite que containers conectados a ela se encontrem pelo nome do container e se comuniquem nas portas internas. Isso evita configurar a aplicação para usar um IP que pode mudar. A porta publicada no host serve para clientes no host; containers da mesma rede podem usar a porta interna do serviço.

```sh
docker network create estudo-net
docker run -d --name estudo-db --network estudo-net \
  -e POSTGRES_PASSWORD=local-only \
  -e POSTGRES_DB=estudo \
  -v estudo_pg:/var/lib/postgresql \
  postgres:18
```

Uma aplicação na mesma rede pode usar host `estudo-db` e porta `5432`. Uma aplicação executada diretamente no host geralmente usa `localhost` e a porta publicada. Credenciais e portas devem ser configuradas para o contexto certo.

Containerização melhora a repetibilidade do ambiente, mas não garante segurança, alta disponibilidade ou recuperação de dados. Restrinja portas, evite segredos na imagem, use imagens apropriadas e mantenha backup separado. A unidade 10.2 aprofunda a execução coordenada com Compose.

**Erro comum:** usar `localhost` dentro do container da aplicação esperando alcançar outro container; nesse contexto, localhost aponta para o próprio container.

