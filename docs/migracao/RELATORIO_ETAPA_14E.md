# Relatório — Etapa 14E

## Resultado

Implementados contratos Pydantic isolados para seis tipos de atividade, projeções pública e privada, validação de coleções e adaptação experimental dos resultados da 14D. A conversão foi executada em memória para 501 questões com gabarito e cinco revisões sem gabarito. Não houve persistência, publicação, importação ou acesso ao MongoDB.

O protótipo preserva os 143 candidatos anteriores e mantém os 358 casos sem conversão objetiva como itens tipados e rastreáveis. Nenhum item foi marcado como `publishable` ou `published`.

## Cobertura classificada

| Tipo tipado | Questões com gabarito | Sem gabarito | Estado dominante |
|---|---:|---:|---|
| Múltipla escolha | 155 | 0 | 143 estruturalmente validadas; 11 com chave ambígua; 1 incompleta |
| Resposta curta | 314 | 0 | Revisão pendente; sem correção automática |
| Discursiva | 23 | 0 | Revisão pendente; sem correção automática |
| Associação | 4 | 0 | Estrutura de pares não extraída; incompleta |
| Ordenação | 4 | 0 | Itens e sequência correta não extraídos; incompleta |
| Revisão | 1 | 5 | Sem pontuação; R1–R5 permanecem sem chave |
| **Total** | **501** | **5** | **506 registros tipados em memória** |

Dos 501 itens com gabarito, 143 continuam candidatos compatíveis com o schema e o corretor objetivo atuais. Os outros 358 permanecem rastreáveis: 314 respostas abertas, 23 exercícios discursivos, oito atividades de associação/ordenação, uma revisão, uma múltipla escolha incompleta e 11 chaves sem alternativa única.

O CSV [CLASSIFICACAO_ATIVIDADES_14E.csv](CLASSIFICACAO_ATIVIDADES_14E.csv) contém 506 linhas de inventário. Registra identidade, tipo, estado, proveniência e diagnóstico; não contém enunciados, respostas, explicações, critérios ou rubricas.

## Contratos e validação

- `backend/curriculum_contract/typed_activities.py` define modelos públicos distintos para múltipla escolha, resposta curta, discursiva, associação, ordenação e revisão.
- Modelos privados tipados preservam gabaritos, explicações, critérios e rubricas quando fornecidos. Campos de resposta ficam fora de `repr` e de todo payload público.
- A serialização pública usa allowlist; o serializador privado é explícito. A serialização canônica interna contém dados privados e não deve ser registrada em logs ou entregue ao aluno.
- IDs, versões de origem, hashes SHA-256, proveniência, opções repetidas, relações, estado e compatibilidade com avaliador são validados.
- Tipos ou sinais de origem desconhecidos falham fechados; não há fallback para teoria nem inferência de conteúdo.
- Os 143 candidatos usam somente a política objetiva já existente: correção no servidor, três tentativas, corte de 70%, melhor nota e revisão após a terceira. A validação estrutural não os torna publicáveis.
- Respostas curtas, discursivas, associação e ordenação recebem política `undecided`; revisões recebem `unscored`. Não há correção automática para esses tipos.

## Fidelidade e limitações

O texto original do bloco permanece no registro interno como `source_markdown`; a projeção pública contém apenas o prompt e, quando a separação foi inequívoca, alternativas ordenadas. Respostas e explicações originais ficam no modelo privado. As cinco revisões R1–R5 não têm objeto privado de gabarito, não têm nota e não entram no corretor.

O contrato tem campos para itens de associação, itens de ordenação, critérios privados e referências curriculares. A conversão atual deixa essas estruturas vazias quando a fonte não fornece uma decomposição comprovável. O `QuizBlock` existente não oferece uma coleção própria de referências; texto de referência que apareça no enunciado continua preservado literalmente, sem resolver ou reescrever links.

O `version_ref` público identifica a proveniência da versão do enunciado. O hash da fonte da chave fica privado. A criação do identificador de versão operacional que vincule os snapshots público e privado depende da persistência futura e não foi implementada.

## Integridade dos artefatos

Hashes conferidos antes e depois:

- Bundle curricular: `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.
- CSV histórico da 14C: `bd8487357aab3e6aa6b4831362ee52b88fa230d1f78c1bc136ae95be60fab89b`.
- CSV histórico da 14D: `ed6e48e675965bb6936a4451372641da212e2589f9696d1bba26acbe18cc10b2`.
- Inventário sanitizado da 14E: `dbdfed7e162116d45aa1b6a95cbb4c08c16c00325e4ef761dee11304857498d4`.

O contrato intermediário, o JSON e as árvores curriculares não foram modificados por esta etapa.

## Verificações

Verificação executada nesta revisão:

- `py -3.13 -m pytest unit_tests/test_typed_activities.py unit_tests/test_experimental_quiz_converter.py unit_tests/test_quiz_grading.py unit_tests/test_curriculum_bulk_import.py -q` — **62 testes aprovados** (inclui 21 testes novos do contrato tipado).
- `py -3.13 -m ruff check curriculum_contract/typed_activities.py unit_tests/test_typed_activities.py` — aprovado.
- `py -3.13 -m ruff format --check curriculum_contract/typed_activities.py unit_tests/test_typed_activities.py` — aprovado.
- `py -3.13 -m mypy --explicit-package-bases --follow-imports=silent curriculum_contract/typed_activities.py unit_tests/test_typed_activities.py` — aprovado para os dois arquivos da 14E.
- `py -3.13 -m py_compile curriculum_contract/typed_activities.py unit_tests/test_typed_activities.py` — aprovado.
- `git diff --check` — sem erros de whitespace; Git emitiu apenas aviso de conversão LF/CRLF já associado ao JSON legado.

A verificação mypy do grafo completo, sem silenciar imports, ainda reporta 13 erros em `database.py`, `audit.py`, `services/common.py`, `services/auth.py`, `learning.py` e `integrity.py`. São módulos fora do escopo da 14E; não foram alterados para esta etapa. O comando direto sem `--explicit-package-bases` também não é aplicável neste layout, pois encontra `curriculum_contract` sob dois nomes de módulo. A verificação focal com bases explícitas passou. O verificador de formatação informou acesso negado ao cache Ruff preexistente, mas terminou com código zero e confirmou que os dois arquivos estão formatados.

Os testes são offline e não acessam banco, importador ou publicação. A validação prova os contratos e a conversão experimental, não a persistência, revisão editorial ou publicação operacional.

## Decisões e próximos passos

Continuam pendentes: política editorial para as cinco perguntas de revisão e para atividades discursivas; critérios de publicação; persistência privada e versionamento de quiz; modelo de correção de associação/ordenação; e resolução de referências editoriais. A próxima etapa deve aprovar esses contratos antes de qualquer implementação persistente. Não há autorização para publicar ou importar estas atividades.
