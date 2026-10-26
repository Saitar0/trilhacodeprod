# Regras aprovadas — migração estrutural da Fase 1

## Escopo e precedência
- Executar somente a Fase 1 em Conteudos_migrado/Fase_1/.
- O checkout original, Conteudos/, JSON de importação, backups e Conteudos/Arquivo/ permanecem intocados.
- Fonte de conteúdo: arquivos Markdown originais da Fase 1. O manifesto aprovado mapeia bloco de origem para destino.
- Não escrever, resumir, corrigir ou expandir conteúdo. Só mover e separar. Preservar rubricas existentes e seus valores.
- Sem commits automáticos; JSON/importador não são executados nem modificados.

## Estrutura
- Caminho: Fase_1/<id>_<slug original>/.
- README.md é índice e conserva o frontmatter original da unidade.
- Objetivo, resumo, critério de conclusão, conexões e referências ficam em arquivos separados.
- Pastas de assunto são planas. README por assunto não é criado.
- Itens compartilhados têm um único arquivo físico sob 90_integracao/ e associações por referência na cobertura.
- Gabaritos, rubricas e checklists existentes ficam em arquivos separados. Não criar arquivos sem bloco de origem, exceto README de índice/metadados autorizado.
- Projetos usam arquivos planos de marcos; aceite em checklist; manter escalas originais.

## Classificação e exceções aprovadas
- Usar os slugs literais registrados em mapa_de_migracao.yml. Em 2.1: 01_terminal_e_caminhos, 02_operacoes_de_arquivo, 03_inspecao_e_busca, 04_entrada_saida_e_pipes.
- 1.2 Q5 e P2 são compartilhados conforme o manifesto, cada um com um único destino físico em 90_integracao/.
- 2.2 Q5 é compartilhado por usuários/permissões e processos/serviços, em um arquivo físico de integração.
- 3.2 P3 é exclusivo de 01_integracao_e_mensagens_commit; manter inclusive cabeçalhos repetidos.
- 3.5 conserva os quatro blocos de teoria, na ordem e texto originais, em teoria_contexto.md.
- Em conexoes.md, manter um único tipo de relação por unidade relacionada. Remoções específicas já aprovadas estão anotadas no manifesto.
- Não remover nem reescrever cabeçalhos repetidos.

## Metadados e links
- Preservar todos os valores YAML atuais da unidade em README.md, sem duplicar key ou estimativa_minutos nos filhos.
- Cada filho recebe arquivo_id global único, parent_key, tipo_arquivo e assunto/ordem quando aplicável.
- Tipos de bloco: quiz, practice, answer_key, answer_key_pratica, rubric, checklist, theory, milestone.
- O vault root Obsidian ainda deve ser confirmado antes de escrever wikilinks. README/index e conexões guardam destinos no manifesto até essa confirmação.
- O JSON futuramente gerado mantém answer_key dentro de theory_text até a extensão separada de importador/renderer.

## Validação
- Comparar blocos reais: normalizar apenas delimitadores de seção/frontmatter autorizados; conteúdo textual deve ser idêntico à origem.
- Verificar cobertura origem→destino para teoria, quiz, respostas, práticas, rubricas, checklists, comuns e conexões.
- Conferir arquivos sem origem, destinos repetidos para itens compartilhados, YAML, IDs únicos, links e hashes dos originais/JSON.