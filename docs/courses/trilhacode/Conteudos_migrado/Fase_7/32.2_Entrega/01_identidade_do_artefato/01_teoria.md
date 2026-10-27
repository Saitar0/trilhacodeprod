---
arquivo_id: "f7-32-2-01-identidade-do-artefato-01-teoria-md"
parent_key: "32.2"
tipo_arquivo: "theory"
assunto: "01_identidade_do_artefato"
ordem: 1
itens_origem: ["### Microtópico 1 — Construa uma vez e identifique o artefato"]
---

### Microtópico 1 — Construa uma vez e identifique o artefato

Um pipeline de entrega começa com uma versão de código identificável, executa validações e produz um **artefato**: por exemplo, um pacote web ou uma imagem de container. O artefato deve ter identidade rastreável, como commit/tag e, quando aplicável, digest. A equipe consegue então responder: qual código originou esta implantação e qual saída foi publicada?

Construa o artefato depois dos checks e promova essa mesma saída entre ambientes. Não rode um build independente para staging e outro para produção sem controlar diferenças: dependências, relógio, configuração ou fontes externas podem gerar resultados distintos. Configuração específica do ambiente deve ser injetada no deploy ou em runtime, sem alterar silenciosamente o conteúdo do artefato. Secrets não devem ser embutidos no pacote cliente.

No GitHub Actions, artefatos de workflow podem passar arquivos de um job para outro e persistir após a execução. São diferentes de caches: use cache para acelerar dados regeneráveis, artefato para transportar o resultado de build/teste. O job de deploy deve baixar o artefato produzido pelo job de build da execução correspondente e registrar commit, nome/digest e ambiente.

