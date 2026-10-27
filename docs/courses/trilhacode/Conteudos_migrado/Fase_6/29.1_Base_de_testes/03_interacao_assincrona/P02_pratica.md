---
arquivo_id: "f6-29-1-03-interacao-assincrona-p02-pratica-md"
parent_key: "29.1"
tipo_arquivo: "practice"
assunto: "03_interacao_assincrona"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Cubra estados assíncronos de uma lista
**Objetivo:** verificar como a interface responde a carregamento, sucesso, vazio e erro de uma consulta.

**Passos:**
1. Escolha uma lista carregada por uma função de API ou serviço isolável.
2. Controle essa fronteira para fornecer uma resposta lenta e depois uma resposta com itens; confirme o indicador e o conteúdo final.
3. Forneça uma lista vazia e confira a mensagem contextual de estado vazio.
4. Rejeite a consulta e verifique a mensagem de erro e a ação de recuperação apresentada.
5. Aguarde mudanças assíncronas com `findBy...` ou uma espera explícita adequada; evite atrasos fixos sem relação com a condição esperada.

**Dica:** cada caso deve começar com estado independente e resultado controlado. Não dependa de uma API externa ou da rede real para decidir o resultado do teste.

**Entrega:** testes determinísticos para carregamento, sucesso, vazio e erro.

**Critérios de conclusão:** todos os estados são percebidos pelo usuário; a falha não é confundida com vazio; os casos podem rodar em qualquer ordem.

