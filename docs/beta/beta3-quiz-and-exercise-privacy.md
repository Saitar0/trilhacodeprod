# Beta 3 — privacidade de quiz e exercícios

## Quiz versionado

As cinco perguntas da unidade 1.1 são convertidas em bloco `quiz` com `activity_schema_version=1`, `prompt`, opções `{id,label}`, `correct_option_id` e `feedback`. IDs são determinísticos. O serviço existente `services.activity_publications.normalize_quiz` validou o contrato; `public_activity` retorna pergunta/opções e parâmetros públicos, excluindo gabarito e feedback. `services.nodes._student_block` também remove esses campos de uma projeção do bloco.

O teste persistentemente leu o bloco via `nodes.get_node` como staff sintético e verificou o gabarito na representação restrita. A trilha permaneceu privada/em draft e a leitura pelo serviço como estudante retornou 404. Isso verifica os serviços exercitados, não a rota HTTP, publicação, frontend, cache ou todas as combinações de autenticação. Não houve publicação da unidade.

O quiz é armazenado com gabarito no documento draft do banco descartável. O contrato de leitura pública que contém a resposta foi testado offline. A segurança do endpoint real do estudante depende também dos estados de publicação; não se pode concluir que gabaritos ficam protegidos em qualquer futura configuração operacional. A metadata genérica de bloco não declara todos os campos versionados e avisa sobre eles; o validador de atividade versionada rejeita campos desconhecidos sem ecoar seus valores.

A fonte contém uma explicação geral por questão, não explicações diferentes para acerto/erro; o adaptador a coloca nos dois slots de feedback. Leitura estática de `services.activities` mostra que a tentativa criada não inclui feedback e que a avaliação só inclui a explicação para acerto ou quando não restam tentativas, caso contrário usa mensagem genérica. Esse endpoint não foi executado nesta fase; o mapeamento precisa de aprovação de produto/avaliação antes de publicação.

## Exercícios manuais

Os três enunciados são enviados ao importador com `grading=manual`. Respostas de referência e critérios ficam somente no contrato intermediário restrito e não são enviados ao banco, porque `exercise_open`/leitor comum não oferecem ACL de instrutor demonstrada para `criteria` ou `rubric`. As projeções explícitas `student_projection()` e `restricted_projection()` permitem testar a separação de campos, mas a segunda não autentica nem autoriza o chamador.

Nenhum executor ou corretor automático é criado. A submissão, fila de revisão humana e feedback real não foram exercitados nesta prova.

## Regras para uma integração futura

1. Nunca serializar o contrato intermediário completo como resposta pública.
2. Selecionar projeções permitidas no backend; ocultar no frontend não é controle.
3. Manter gabarito e feedback restrito fora dos payloads de aluno até o momento permitido por política aprovada.
4. Criar destino com ACL específica para rubricas, respostas-modelo e critérios do corretor; não usar campos genéricos sem autorização de leitura demonstrada.
5. Testar leitor, rota autenticada e publicação versionada com casos de aluno, corretor e acesso revogado.
6. Não incluir respostas, tokens, payloads privados ou segredos nas mensagens de erro/logs.

Retenção de conteúdo restrito e política de feedback após correção permanecem decisões humanas pendentes.
