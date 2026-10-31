# Beta 4 — validação de quizzes e exercícios

## Totais e representação

O lote contém 30 arquivos de autoria de quiz que produziram 44 questões tipadas, e 26 exercícios manuais. A unidade 3.5 contém projeto com marcos, não um quiz ou exercício convencional; seus 11 artefatos de projeto permanecem fora do payload. A unidade 3.4 demonstra cardinalidade diferente do padrão: quatro questões e duas práticas.

Cada questão preserva ID de origem, ordem, enunciado, alternativas, opção correta, explicação e associação temática quando presente. Cada exercício preserva ID, título, instruções, ordem, hash de fonte e vínculo à unidade. A representação não executa código nem cria correção automática.

## Privacidade

O gabarito é material de autoria restrito. O payload mantém campos corretos apenas no bloco de quiz draft dentro do banco de teste. O teste consultou os blocos pelo `get_node` real e aplicou o helper real `_student_block`, verificando que `correct_option_id`, `feedback` e `explanation` são removidos. A trilha permaneceu privada e draft, e o serviço real negou leitura ao ator estudante sintético com 404.

Isso não comprova que respostas estejam protegidas em uma rota publicada, em todos os endpoints ou por uma ACL de instrutor. Não houve publicação nem chamada HTTP. Respostas de referência, rubricas, checklists e project keys não foram incluídos no payload nem nos manifestos. O contrato distingue o material intermediário privado, mas nenhuma persistência segura dessas chaves foi validada.

## Compatibilidade de avaliação

Os tipos de bloco atuais aceitam `quiz` e `exercise_open`; o importador real aceitou o payload em draft. O serviço de submissão/progresso não foi exercitado nesta prova. Falta demonstrar versão imutável de quiz vinculada a uma geração publicada, armazenamento protegido de resposta/rubrica, timing do feedback e a jornada do aluno. A aprovação pedagógica dos gabaritos permaneceu fora do escopo técnico; a conversão só preservou os textos fonte e seus hashes.
