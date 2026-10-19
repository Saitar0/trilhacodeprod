---
title: "Fase 1 — Base técnica e alfabetização de desenvolvimento"
aliases:
  - Fase 1
tags:
  - trilhas
  - fase
tipo: fase
ordem: 1
trilha: "[[00_Trilha_Full_Stack_Estruturada]]"
status: nao-iniciada
---

# Fase 1 — Base técnica e alfabetização de desenvolvimento

Parte da trilha [[00_Trilha_Full_Stack_Estruturada|Desenvolvimento de Software — Full Stack e Engenharia]].

## Objetivo
Construir a base técnica para estudar com autonomia: entender como software e web funcionam, operar o terminal e versionar o trabalho com Git e GitHub.

## Por que esta fase vem agora?
Todas as fases seguintes pressupõem um ambiente funcional, domínio mínimo do terminal e o hábito de versionar o que se estuda.

## Pré-requisitos
Nenhum além de um computador com acesso à internet.

## Competências
- Explicar como cliente, servidor e banco de dados se relacionam
- Operar o terminal para navegar, inspecionar processos e logs
- Acessar servidores remotos e o GitHub com chaves SSH
- Versionar código com histórico legível e colaborar por pull requests

## Projeto incremental
Dotfiles e setup do ambiente versionados e repositório de estudos com README e histórico limpo; esse repositório é a base dos projetos das fases seguintes. Detalhado em [[Fase_1_Base_Tecnica#3.5 — Projeto incremental da fase|3.5 Projeto incremental da fase]].

## Critério de conclusão
Um repositório de estudos com README e histórico limpo e um ambiente de desenvolvimento documentado e reproduzível.

## Estimativa de carga horária

**Total estimado da fase:** 16,5–30 h (referência de planejamento: 23 h), somando estudo das unidades e projeto(s) desta fase. As faixas incluem estudo, prática, correção e revisão; consulte [[Estimativa_de_Carga_Horaria|metodologia e estimativas detalhadas]].

## Módulos
- [[#Módulo 1 — Computação e ambiente de desenvolvimento|Módulo 1 — Computação e ambiente de desenvolvimento]]
- [[#Módulo 2 — Terminal, sistema operacional e acesso remoto|Módulo 2 — Terminal, sistema operacional e acesso remoto]]
- [[#Módulo 3 — Git e GitHub|Módulo 3 — Git e GitHub]]

---

## Módulo 1 — Computação e ambiente de desenvolvimento

**Objetivo:** Entender o que é software, como um programa é executado e como cliente, servidor e banco de dados se relacionam na web. Ao final, você deverá conseguir narrar o caminho de uma ação no navegador até a resposta exibida, usando corretamente os termos requisição, resposta, HTTP, DNS e API.

**Submódulos:** [[Fase_1_Base_Tecnica#1.1 — Computação e software|1.1 Computação e software]] · [[Fase_1_Base_Tecnica#1.2 — Ambiente de desenvolvimento|1.2 Ambiente de desenvolvimento]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 1.1 — Computação e software

**Classificação:** `integrado` · `obrigatorio` · `media` · #fundamentos #web

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Entender o que é software, como um programa é executado e como cliente, servidor e banco de dados se relacionam na web. Ao final, você deverá conseguir narrar o caminho de uma ação no navegador até a resposta exibida, usando corretamente os termos requisição, resposta, HTTP, DNS e API.

**Tópicos:**
- [ ] o que é software
- [ ] o que é programa
- [ ] como um programa é executado
- [ ] diferença entre frontend, backend e banco de dados
- [ ] diferença entre aplicação local e aplicação na web
- [ ] cliente e servidor
- [ ] navegador e servidor
- [ ] requisição e resposta
- [ ] noção de HTTP
- [ ] noção de DNS
- [ ] noção de APIs

**Atividade prática:** Escolha uma página que você usa e represente, em um diagrama, o que acontece quando você a abre. Inclua cliente/navegador, DNS, servidor, requisição, resposta, frontend, backend e banco de dados quando fizerem parte do fluxo.

**Critério de conclusão:** Sem consultar o material, a pessoa consegue explicar a diferença entre frontend, backend e banco de dados; narrar o fluxo navegador → DNS → requisição/resposta HTTP → página; e explicar para que serve uma API. O diagrama deve mostrar corretamente cliente e servidor e não tratar DNS como armazenamento ou banco de dados como etapa obrigatória de toda navegação.

**Relações:** Complementar: [[Fase_1_Base_Tecnica#1.2 — Ambiente de desenvolvimento|1.2]] · Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#7.3 — Dados e comunicação|7.3]], [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]]

### 1.2 — Ambiente de desenvolvimento

**Classificação:** `solo` · `obrigatorio` · `media` · #ferramentas #fundamentos

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Preparar um ambiente de trabalho funcional, entender arquivos e pastas, usar um editor e terminal, instalar ferramentas com cuidado, compreender variáveis de ambiente e consultar documentação técnica.

**Pré-requisitos:** - Pré-requisito: [[Fase_1_Base_Tecnica#1.1 — Computação e software|1.1 — Computação e software]]

**Tópicos:**
- [ ] sistema de arquivos
- [ ] pastas e arquivos
- [ ] extensões de arquivo
- [ ] editor de código
- [ ] terminal
- [ ] variáveis de ambiente
- [ ] instalação de ferramentas
- [ ] leitura de documentação técnica básica
- [ ] WSL (para quem usa Windows)

**Atividade prática:** Crie um documento de setup para uma máquina nova. Registre sistema e versão, editor, terminal/shell, ferramentas essenciais, passos de instalação e um comando ou ação que confirme cada ferramenta. Inclua uma nota de segurança explicando onde credenciais não devem ser guardadas. Se usa Windows e optar por WSL, identifique explicitamente essa rota; caso contrário, registre a rota escolhida.

**Critério de conclusão:** Reproduzir o ambiente em outra máquina seguindo apenas a documentação escrita, explicar caminhos e variáveis de ambiente em nível básico e identificar a fonte oficial usada para instalar ou configurar cada ferramenta.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#1.1 — Computação e software|1.1]], [[Fase_5_Backend_e_Arquitetura#20.2 — Segurança básica|20.2]] · Complementar: [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1]]

---

## Módulo 2 — Terminal, sistema operacional e acesso remoto

**Objetivo:** Navegar e manipular arquivos pelo terminal com caminhos absolutos e relativos, visualização, redirecionamento, pipes e busca com `find`, preservando os dados que não pretende alterar.

**Submódulos:** [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1 Terminal e navegação]] · [[Fase_1_Base_Tecnica#2.2 — Sistema e operação|2.2 Sistema e operação]] · [[Fase_1_Base_Tecnica#2.3 — Acesso remoto|2.3 Acesso remoto]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 2.1 — Terminal e navegação

**Classificação:** `pratica` · `obrigatorio` · `alta` · #ferramentas #fundamentos

**Carga horária estimada:** 2,5 h–4,5 h (referência: 3,5 h).

**Objetivo:** Navegar e manipular arquivos pelo terminal com caminhos absolutos e relativos, visualização, redirecionamento, pipes e busca com `find`, preservando os dados que não pretende alterar.

**Tópicos:**
- [ ] navegação por diretórios
- [ ] criar, mover, copiar e apagar arquivos
- [ ] caminhos absolutos e relativos
- [ ] visualização de conteúdo
- [ ] redirecionamento básico
- [ ] pipes
- [ ] find

**Atividade prática:** Em uma pasta temporária criada para o exercício, monte `estudo/{entrada,docs,saida}`. Crie três arquivos Markdown em `entrada`, copie um para `docs`, renomeie outro, mova o terceiro para `saida`, inspecione um arquivo e encontre todos os `.md` com `find`. Grave a lista encontrada em `saida/lista.txt` e depois acrescente uma linha manual usando o redirecionamento apropriado. Repita a busca sem usar a interface gráfica.

**Critério de conclusão:** Executar tarefas de criação, cópia, movimentação, inspeção, busca e redirecionamento usando caminhos corretos; explicar a diferença entre `>` e `>>` e entre redirecionamento e pipe; evitar alterações fora da pasta de exercício.

**Relações:** Complementar: [[Fase_1_Base_Tecnica#1.2 — Ambiente de desenvolvimento|1.2]] · Relacionado: [[Fase_1_Base_Tecnica#3.1 — Git local|3.1]]

### 2.2 — Sistema e operação

**Classificação:** `solo` · `obrigatorio` · `media` · #fundamentos #ferramentas

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Entender usuários, permissões, processos, serviços e logs; usar `grep` e `tail` para investigar um problema simples e reconhecer quando uma operação exige privilégios ou pode afetar o sistema.

**Pré-requisitos:** - Pré-requisito: [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1 — Terminal e navegação]]

**Tópicos:**
- [ ] permissões
- [ ] usuários
- [ ] processos
- [ ] serviços
- [ ] logs
- [ ] grep
- [ ] tail
- [ ] chmod e chown

**Atividade prática:** Crie `app.log` com linhas fictícias em horários diferentes, incluindo inicialização, uma operação bem-sucedida e um erro de permissão. Use `tail` para observar o final do arquivo e `grep` para localizar erro e contexto relevante. Escreva um relatório curto com horário, processo, mensagem, hipótese e próxima verificação. Não altere permissões reais da máquina.

**Critério de conclusão:** Explicar como permissões podem impedir uma operação, distinguir processo e serviço, e localizar em um log uma mensagem relacionada a uma falha sem expor dados sensíveis.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1]], [[Fase_5_Backend_e_Arquitetura#17.2 — Depuração no servidor|17.2]], [[Fase_4_Dados_e_Bancos#10.1 — Containerização|10.1]], [[Fase_8_Infra_Operacao#38.1 — Sinais operacionais|38.1]]

### 2.3 — Acesso remoto

**Classificação:** `solo` · `obrigatorio` · `media` · #ferramentas

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Explicar o propósito do SSH, conectar-se a um servidor remoto com segurança e configurar uma chave para autenticar no GitHub, sem compartilhar a chave privada.

**Pré-requisitos:** - Pré-requisitos: [[Fase_1_Base_Tecnica#1.1 — Computação e software|1.1 — Computação e software]] e [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1 — Terminal e navegação]]

**Tópicos:**
- [ ] o que é SSH
- [ ] conexão SSH
- [ ] chaves SSH
- [ ] uso com GitHub
- [ ] noção de servidor remoto

**Atividade prática:** Siga a documentação oficial para conferir se já possui uma chave, gerar uma se necessário, proteger a chave privada, cadastrar a pública e testar a conexão. Não cole nenhum segredo no material do curso. Depois, confira em um repositório de teste se o endereço remoto começa no formato SSH e descreva o que muda em relação ao HTTPS.

**Critério de conclusão:** Autenticar por chave SSH no GitHub e explicar o papel de cada chave, como proteger a privada e a diferença entre chave SSH e token de aplicação.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#1.1 — Computação e software|1.1]], [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1]], [[Fase_5_Backend_e_Arquitetura#20.1 — Autenticação|20.1]], [[Fase_7_Infra_Deploy_e_Cloud#34.1 — Base de cloud|34.1]] · Complementar: [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3]]

---

## Módulo 3 — Git e GitHub

**Objetivo:** Criar um repositório Git, registrar alterações em commits, trabalhar com branches e inspecionar ou desfazer mudanças com segurança.

**Submódulos:** [[Fase_1_Base_Tecnica#3.1 — Git local|3.1 Git local]] · [[Fase_1_Base_Tecnica#3.2 — Trabalho com histórico|3.2 Trabalho com histórico]] · [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3 GitHub]] · [[Fase_1_Base_Tecnica#3.4 — Revisita contínua|3.4 Revisita contínua]] · [[Fase_1_Base_Tecnica#3.5 — Projeto incremental da fase|3.5 Projeto incremental da fase]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 3.1 — Git local

**Classificação:** `solo` · `obrigatorio` · `alta` · #ferramentas

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Criar um repositório Git, registrar alterações em commits, trabalhar com branches e inspecionar ou desfazer mudanças com segurança.

**Pré-requisitos:** - Pré-requisito: [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1 — Terminal e navegação]]

**Tópicos:**
- [ ] init
- [ ] status
- [ ] add
- [ ] commit
- [ ] log
- [ ] diff
- [ ] restore
- [ ] reset
- [ ] branch
- [ ] .gitignore

**Atividade prática:** Em uma pasta de exercício, inicialize um repositório. Crie `README.md` e `.gitignore`, faça um commit inicial, depois altere os dois arquivos de maneiras diferentes. Use `status` e `diff` para selecionar apenas a mudança do README; confira o staging; faça um commit. Crie uma branch, registre uma alteração nela e retorne à branch inicial. Use `git log --all --oneline --graph --decorate` para inspecionar o histórico e visualizar a branch concluída. Por fim, demonstre como retirar do staging um ...

**Critério de conclusão:** Explicar working tree, staging area e repositório, criar commits e branches e escolher uma operação segura para desfazer uma mudança, descrevendo antes o estado que será afetado.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1]] · Complementar: [[Fase_1_Base_Tecnica#3.2 — Trabalho com histórico|3.2]]

### 3.2 — Trabalho com histórico

**Classificação:** `solo` · `obrigatorio` · `media` · #ferramentas

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Integrar mudanças com merge, rebase e cherry-pick, resolver conflitos e escrever mensagens de commit que expliquem a intenção da mudança.

**Pré-requisitos:** - Pré-requisito: [[Fase_1_Base_Tecnica#3.1 — Git local|3.1 — Git local]]

**Tópicos:**
- [ ] merge
- [ ] rebase
- [ ] cherry-pick
- [ ] resolução de conflitos
- [ ] boas mensagens de commit

**Atividade prática:** Em um repositório descartável, crie uma branch e altere uma linha de um arquivo. Na branch principal, altere a mesma linha de outra forma. Tente integrar, examine os marcadores e resolva o conflito preservando a intenção de ambas as mudanças quando possível. Registre a resolução em commit. Em seguida, compare os históricos resultantes de merge e rebase em uma segunda cópia do exercício.

**Critério de conclusão:** Explicar merge, rebase e cherry-pick com um caso de uso para cada; resolver um conflito e justificar a solução; reconhecer o risco de reescrever commits já compartilhados.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#3.1 — Git local|3.1]] · Complementar: [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3]]

### 3.3 — GitHub

**Classificação:** `pratica` · `obrigatorio` · `alta` · #ferramentas

**Carga horária estimada:** 2,5 h–4,5 h (referência: 3,5 h).

**Objetivo:** Publicar um repositório no GitHub, sincronizar mudanças com `clone`, `fetch`, `pull` e `push`, colaborar por pull requests e revisão, organizar o projeto e manter segredos fora do histórico.

**Pré-requisitos:** - Pré-requisitos: [[Fase_1_Base_Tecnica#2.3 — Acesso remoto|2.3 — Acesso remoto]] e [[Fase_1_Base_Tecnica#3.1 — Git local|3.1 — Git local]]

**Tópicos:**
- [ ] repositórios remotos
- [ ] push
- [ ] pull
- [ ] fetch
- [ ] clone
- [ ] pull requests
- [ ] code review
- [ ] GitFlow
- [ ] organização de repositórios
- [ ] segredos e credenciais fora do repositório

**Atividade prática:** Crie um repositório de estudo sem dados sensíveis, clone-o, faça uma branch e altere o README. Envie a branch e abra uma PR para a branch principal. Peça revisão a alguém; se estiver trabalhando sozinho, revise o diff pela aba de arquivos alterados e registre na descrição da PR uma observação concreta e a melhoria feita. Responda ao feedback recebido e integre a mudança conforme as permissões do repositório.

**Critério de conclusão:** Conduzir o fluxo clone → branch → commit → push → pull request → revisão → integração, explicar a diferença entre fetch e pull e demonstrar como prevenir e responder à exposição de credenciais.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#2.3 — Acesso remoto|2.3]], [[Fase_1_Base_Tecnica#3.1 — Git local|3.1]], [[Fase_7_Infra_Deploy_e_Cloud#32.1 — Automação|32.1]] · Complementar: [[Fase_1_Base_Tecnica#3.2 — Trabalho com histórico|3.2]]

### 3.4 — Revisita contínua

**Classificação:** `revisita` · `obrigatorio` · `media` · #ferramentas #qualidade

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Manter estudos e projetos versionados, revisar periodicamente o histórico, remover branches concluídas quando seguro e organizar um README em inglês que permita entender o repositório.

**Pré-requisitos:** - Pré-requisitos: [[Fase_1_Base_Tecnica#3.2 — Trabalho com histórico|3.2 — Trabalho com histórico]] e [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3 — GitHub]]

**Tópicos:**
- [ ] versionar todo estudo daqui para frente
- [ ] revisão de histórico
- [ ] limpeza de branches
- [ ] organização de README
- [ ] commits, README e issues escritos em inglês

**Atividade prática:** Abra seu repositório de estudos e revise o estado, o histórico recente, branches locais e README. Escolha um commit vago para corrigir apenas se ainda for seguro e não tiver sido compartilhado; caso contrário, registre a convenção a adotar daqui em diante. Atualize o README em inglês com objetivo, estrutura, requisitos e instruções de uso. Liste branches que podem ser removidas e justifique que o trabalho está preservado.

**Critério de conclusão:** Manter o repositório de estudos organizado, com README em inglês que permita a outra pessoa entender e usar o conteúdo, histórico legível e branches concluídas tratadas sem perda de trabalho.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#3.2 — Trabalho com histórico|3.2]], [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3]]

### 3.5 — Projeto incremental da fase

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto

**Carga horária estimada:** 4 h–6 h (referência: 5 h).

**Objetivo:** Criar a base de trabalho que acompanhará o curso: escolher uma ideia para o projeto acumulado, documentar o ambiente, versionar uma parte segura do setup e manter um repositório de estudos com README e histórico legível.

**Pré-requisitos:** - Pré-requisitos: [[Fase_1_Base_Tecnica#3.1 — Git local|3.1 — Git local]], [[Fase_1_Base_Tecnica#3.2 — Trabalho com histórico|3.2 — Trabalho com histórico]] e [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3 — GitHub]]

**Tópicos:**
- [ ] dotfiles e setup do ambiente versionados
- [ ] repositório de estudos com README e histórico limpo
- [ ] escolher a ideia do Trilho A entre 3 candidatos (gestor de tarefas, loja virtual ou base de conhecimento)

**Atividade prática:** Crie o repositório que acompanhará as próximas fases. Escreva o README em inglês simples com propósito, ideia escolhida, estrutura atual, requisitos e passos para preparar o ambiente. Documente o setup em `setup/README.md` ou em uma seção equivalente. Selecione apenas configurações que possam ser compartilhadas com segurança, adicione `.gitignore` apropriado e faça commits pequenos. Revise o repositório local e a cópia remota antes de considerar a entrega pronta.

**Critério de conclusão:** Uma pessoa consegue compreender a ideia escolhida, preparar o ambiente seguindo a documentação e navegar pelo repositório; o histórico é legível e não há credenciais ou dados pessoais versionados.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#3.1 — Git local|3.1]], [[Fase_1_Base_Tecnica#3.2 — Trabalho com histórico|3.2]], [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3]] · Complementar: [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3]]
