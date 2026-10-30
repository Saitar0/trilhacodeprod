# Contrato frontend de atividades — Etapa 14G

## Entrada pública

TypedActivityRenderer recebe activity: unknown; o parser produz uma variante discriminada pelo campo type:

- multiple_choice: options ordenadas com option_id e text.
- short_answer: enunciado e instruções.
- discursive: enunciado e instruções.
- matching: left_items e right_items, cada item com ref e text.
- ordering: items com ref e text.
- review: pergunta de revisão sem pontuação.

A base segue os campos públicos do contrato 14E: activity_ref, version_ref, title, order, prompt, instructions e references.

## Validação

O parser verifica IDs curriculares e versão de origem, texto, ordenação, tipo, cardinalidade de alternativas e unicidade de referências/IDs. Cada objeto é copiado para uma forma allowlisted. Campos adicionais são rejeitados, especialmente correct_option_ref, correct_index, answer_key, explanation, private ou equivalentes. Tipos desconhecidos e objetos incompletos produzem estado de erro acessível.

## Props de apresentação

- activity: payload público desconhecido até validação.
- mode: interactive, read_only, unavailable ou error.
- message: mensagem de estado apresentada como texto.

Não existem props para gabarito, correção, nota, callback de progresso, API ou persistência.

## Flag

VITE_TYPED_ACTIVITIES_ENABLED deve ser exatamente true para exibir os controles. Se ausente ou desligada, o renderer mostra o estado desativado. A flag não altera VITE_QUIZ_API_ENABLED, não é definida nos arquivos de ambiente e não é ligada por padrão.

## Interação isolada

As respostas ficam apenas no estado React local e são descartadas ao desmontar o componente. Múltipla escolha não indica acerto/erro. Respostas curtas/discursivas não são comparadas. Matching usa selects; ordenação usa botões de mover, compatíveis com teclado. Revisão é estática e não pontuada.

O texto recebido, inclusive instruções e referências, é renderizado por nós de texto React; não é interpretado como HTML ou Markdown. URLs são apresentadas como texto, não transformadas automaticamente em links navegáveis.

## Limites de responsabilidade

Este é um componente de demonstração isolado. Não consome dados operacionais, não chama API, não cria tentativas, não salva rascunhos, não publica conteúdo e não altera progresso. O limite de caracteres no campo curto e discursivo é uma proteção técnica da interface, não um critério de avaliação.