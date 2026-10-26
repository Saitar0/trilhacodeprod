---
arquivo_id: "f1-2-2-90-integracao-05-pratica-independente-falha-escrita"
parent_key: "2.2"
tipo_arquivo: "practice"
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — investigue uma falha de escrita

O log anterior mostra uma tentativa de escrita em `/srv/app/uploads/relatorio.csv`. A equipe fornece estes dados fictícios:

```text
processo: webapp
grupos efetivos do processo: app-readers
/srv:                drwxr-xr-x root       root
/srv/app:            drwxr-xr-x deploy     deploy
/srv/app/uploads:    dr-xr-x--- deploy     app-readers
```

Considere que os diretórios pais permitem atravessamento e que não há ACLs adicionais neste cenário didático. O processo pertence ao grupo `app-readers`.

**Entregue:**

1. O que os dados permitem afirmar e o que ainda não permitem afirmar.
2. Por que o grupo do processo consegue atravessar e listar `uploads`, mas não criar um arquivo nesse diretório.
3. Uma próxima verificação sobre o comportamento esperado do serviço.
4. Uma proposta de correção mínima, condicionada à confirmação de que o serviço deve gravar ali. Não execute a correção.

**Dicas progressivas**

- Em permissões Unix, para criar ou remover uma entrada em um diretório são relevantes as permissões de escrita e de atravessamento no próprio diretório. A permissão de leitura permite listar nomes; ela não concede escrita.
- Uma hipótese consistente com o log não é prova completa da causa. Verifique o caminho, a identidade efetiva, os grupos e a política pretendida antes de mudar qualquer permissão.

