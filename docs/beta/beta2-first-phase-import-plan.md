# Beta 2 — plano para a primeira fase curricular

## Escopo candidato, ainda sujeito a decisão

O pacote tipado local consultado declara 10 unidades na Fase 1, 43 nós (1 fase, 3 módulos, 10 submódulos/unidades e 29 tópicos), 263 blocos, 1 projeto, 21 relações e 95 placements. Esses números vêm de artefatos locais da migração, incluindo bundle modificado, e são base de planejamento, não inventário aprovado para importação.

Unidades listadas no índice segmentado:

1. 1.1 Computação e software.
2. 1.2 Ambiente de desenvolvimento.
3. 2.1 Terminal e navegação.
4. 2.2 Sistema e operação.
5. 2.3 Acesso remoto.
6. 3.1 Git local.
7. 3.2 Trabalho com histórico.
8. 3.3 GitHub.
9. 3.4 Revisita contínua.
10. 3.5 Projeto incremental.

Tipos globais declarados para esta fase: 44 quizzes, 44 gabaritos, 26 práticas, 10 rubricas, 14 checklists, 10 feedbacks, 10 objetivos, 10 resumos, 10 critérios de conclusão, 30 teorias e 39 referências. Totais incluem a estrutura do contrato tipado e devem ser reconciliados com placements antes da geração do payload final.

## Adaptações necessárias

1. Ratificar fonte/commit e congelar manifestos, IDs e hashes; confirmar os arquivos dirty da migração com seus proprietários.
2. Adaptar o contrato tipado para o contrato de persistência aprovado; não importar diretamente o envelope `IntermediateContract` pelo endpoint legado.
3. Construir árvore completa fase → módulo → unidade → tópico com refs estáveis e testar relações e ordenação.
4. Definir destinos para objetivo, conclusão, feedback, resposta, solução, rubrica, placements compartilhados, projetos e avisos editoriais; rejeitar campos sem destino, sem perda silenciosa.
5. Separar dados do aluno e do instrutor: resposta correta, soluções e feedback de gabarito não podem entrar em leitores públicos antes da política de publicação.
6. Definir comportamento dos 95 placements da Fase 1 para progresso compartilhado, atualmente `undecided` no bundle local.
7. Restringir importação a draft e trilha privada até validação pedagógica, segurança editorial e aprovação de publicação.
8. Vincular o hash e a revisão do manifesto às entidades persistidas; definir repetição e atualização sem sobrescrever conteúdo editorial divergente.

## Validações antes de qualquer importação operacional

- Dry-run de todos os 10 nós/unidades, 29 tópicos, 263 blocos e relações com comparador de origem/destino.
- IDs globais únicos, refs e destinos existentes; verificação de links, conexões e arquivo estrutural fora do mapeamento.
- Testes de quiz versionado, tentativa e submissão manual; respostas privadas ausentes em resposta de aluno.
- Testes de exercícios, rubrica, gabarito e progresso, incluindo placements compartilhados.
- Testes persistentes de importação idempotente e falha/retomada com transações ou protocolo aprovado; o importador C16 atual não é atomicamente transacional.
- Testes do leitor real e frontend em rascunho/publicado e após alteração de versão.
- Revisão editorial humana e critérios de conclusão aprovados por unidade.
- Autorização, auditoria, CAS/fencing e contenção de writers concorrentes aprovados para integração.

Não converter automaticamente a fase nesta etapa, não importar o bundle dirty, não publicar e não alterar o curso fonte.
