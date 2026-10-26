---
arquivo_id: "f1-3-5-teoria-contexto"
parent_key: "3.5"
tipo_arquivo: "theory"
ordem: 0
itens_origem: ["O repositório como caderno de engenharia", "Escolha de uma ideia para o Trilho A", "Dotfiles e setup seguro", "Critérios de um repositório sustentável"]
---

## Teoria

### O repositório como caderno de engenharia
O repositório de estudos registra exercícios, decisões, referências e pequenas entregas do curso. Organize-o para você conseguir encontrar o que estudou e para outra pessoa entender como começar. Um exemplo de estrutura, adaptável às necessidades reais:

```text
estudos/
├── README.md
├── setup/
│   └── README.md
├── fase-1/
│   ├── ambiente/
│   ├── terminal/
│   └── git/
└── projetos/
    └── trilho-a/
```

Não crie diretórios vazios apenas para preencher uma árvore. Inclua arquivos quando houver conteúdo e revise a estrutura conforme o curso cresce.

### Escolha de uma ideia para o Trilho A
O projeto principal evoluirá durante o curso. Escolha um problema que ainda seja interessante quando ganhar novas funcionalidades, mas que possa começar simples. Três candidatos definidos no roadmap:

- **Gestor de tarefas:** exercita colaboração, organização por usuário ou empresa e fluxos de trabalho.
- **Loja virtual:** exercita catálogo, pedidos e regras transacionais.
- **Base de conhecimento:** exercita conteúdo, busca e evolução para recursos de IA.

Não é necessário desenhar agora a arquitetura final. Registre o problema, quem poderia usá-lo, uma primeira necessidade e por que a ideia combina com o que quer aprender. A escolha pode ser trocada uma única vez até o fim da Fase 4, com o motivo registrado no README, conforme o roadmap.

### Dotfiles e setup seguro
Dotfiles são arquivos de configuração do usuário, frequentemente com nomes iniciados por ponto em sistemas Unix. Versionar configurações pode facilitar a reprodução do ambiente, mas não copie indiscriminadamente sua pasta pessoal. Revise cada arquivo e remova tokens, chaves privadas, caminhos específicos, dados pessoais e configurações que possam prejudicar outra máquina. Prefira documentar o processo e versionar uma seleção pequena e segura.

O setup deve explicar pré-requisitos e passos para criar um ambiente funcional. Separe instruções gerais de preferências pessoais e inclua como verificar que cada ferramenta está disponível. Não inclua estimativas de tempo nesta entrega.

### Critérios de um repositório sustentável
Um bom repositório tem objetivo identificável, instruções que funcionam, organização simples, histórico compreensível e dados sensíveis fora do controle de versão. README não precisa ser longo; precisa responder às perguntas de quem chega. Issues podem registrar próximas etapas, mas não substituem a documentação essencial.

