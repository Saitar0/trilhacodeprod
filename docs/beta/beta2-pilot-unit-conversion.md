# Beta 2 — conversão piloto da unidade 1.1

## Artefatos

- Conversor: `backend/curriculum_contract/experimental_beta_curriculum_converter.py`.
- Fixture independente, original inalterado: `backend/integration_tests/fixtures/beta2/unit_1_1_computacao_e_software.source.md`.
- Manifesto sem conteúdo pedagógico: `docs/beta/beta2-pilot-unit-manifest.json`.
- Testes offline: `backend/unit_tests/test_beta_curriculum_converter.py`.
- Prova persistente do importador/leitores: `backend/integration_tests/test_beta_curriculum_import.py`.

O parser aceita somente a gramática delimitada da unidade piloto: frontmatter simples, seções H2 esperadas, perguntas e alternativas enumeradas, gabarito comentado e referências no padrão observado. Ele falha fechado para seção obrigatória ausente, IDs duplicados, caminho de origem inválido e gabarito/questão incompatível. Seções H2 desconhecidas permanecem no objeto de conversão e geram aviso. Não há escrita na fonte, IA ou reescrita pedagógica.

## Preservação demonstrada

Na saída tipada são preservados título, ID de origem, objetivo, texto integral de teoria, resumo, cinco perguntas com alternativas, resposta e explicação, três práticas, referências, critério de conclusão, conexões literais, metadados e hashes da fonte. IDs de destino são determinísticos a partir de `key` e números de questão/prática/referência. O manifesto lista refs, contagens, versão do conversor, hash bruto e hash normalizado.

No payload C16, teoria e resumo tornam-se blocos separados; quizzes são versionados; práticas são `exercise_open` com correção manual e critérios reconhecidos; objetivo, tags e metadados taxonômicos são mapeados ao nó; referências guardam citação e URL. O payload fixa track privada e todos os estados em `draft`.

## Perdas e limites declarados

- A teoria é condensada em um bloco; a divisão da representação migrada em cinco tópicos e sua ordem de avaliação não são mantidas como nós.
- Critério de conclusão, conexões e descrições das referências não têm destino comprovado e não são persistidos.
- Soluções de exercícios sem destino privado comprovado são deliberadamente omitidas do payload; não se assume que recibos ou campo arbitrário sejam ACL.
- Perguntas e gabaritos de quiz são persistidos como campos privados de bloco em rascunho. O esquema genérico do editor C16 não declara todos os campos versionados e emite warnings. O teste offline confirma a projeção pública sem gabarito, mas nenhuma publicação ou endpoint de aluno foi executado.
- O hash e a revisão da fonte estão no manifesto; o importador legado grava `meta.import_ref`, mas não grava o hash de origem no documento. A ligação persistente entre manifesto e documentos exige adaptador futuro.
- A fonte local e a representação segmentada estão em estado `rascunho`; conversão não é aprovação pedagógica.

Portanto, a conversão preserva conteúdo e rastreabilidade no **resultado experimental**, com campos sem destino explicitados, mas ainda não representa uma transformação integral/lossless pronta para fase completa.
