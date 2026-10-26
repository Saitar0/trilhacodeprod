---
arquivo_id: "f1-2-3-90-integracao-01-pratica-guiada-conexao"
parent_key: "2.3"
tipo_arquivo: "practice"
ordem: 1
itens_origem: ["P1"]
---

## Prática — três níveis

As atividades usam GitHub como exemplo e devem seguir a documentação oficial correspondente ao seu sistema. Nunca inclua chave privada, passphrase ou saída com dados sensíveis em entregas, capturas de tela ou chamados.

### 1. Guiada — classifique os dados de uma conexão

Considere estes elementos de uma configuração fictícia:

```text
~/.ssh/id_ed25519       arquivo da chave privada
~/.ssh/id_ed25519.pub   arquivo da chave pública correspondente
git@github.com:acme/app.git
https://github.com/acme/app.git
SHA256:AbCdEf...        impressão digital apresentada na primeira conexão
```

**Tarefa:** classifique cada elemento como privado, público, endereço SSH, endereço HTTPS ou impressão digital de chave de host. Depois, responda: qual arquivo pode ser cadastrado na conta; qual endereço usa SSH; o que precisa ser confirmado antes de aceitar uma chave de host desconhecida?

