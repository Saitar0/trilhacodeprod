---
arquivo_id: "f5-23-1-02-solid-criterios-design-01-teoria"
parent_key: "23.1"
tipo_arquivo: "theory"
assunto: "02_solid_criterios_design"
ordem: 2
itens_origem: ["Microtópico 3 — SOLID como perguntas de design"]
---

## Microtópico 3 — SOLID como perguntas de design

SOLID é um conjunto de princípios de design orientado a objetos. Use-os como perguntas para encontrar acoplamento ou responsabilidades mal distribuídas, não como uma lista para criar interfaces e classes em cada arquivo.

- **Responsabilidade única:** que tipo de mudança deveria afetar este componente? Separar por motivo de mudança é mais útil do que contar métodos.
- **Aberto/fechado:** uma nova variação recorrente pode ser adicionada sem reescrever uma política central? Não significa proibir toda alteração no código.
- **Substituição de Liskov:** uma implementação substituta respeita as expectativas do contrato? Se o fake aceita dados que o banco rejeita, o teste pode esconder uma diferença importante.
- **Segregação de interfaces:** cada consumidor depende apenas das operações que precisa? Um contrato pequeno tende a ser mais fácil de substituir e entender.
- **Inversão de dependência:** a política de alto nível depende de um contrato estável, em vez de importar diretamente um detalhe volátil? A inversão deve reduzir o acoplamento que importa.

Um princípio não prescreve uma arquitetura completa. Uma interface de uma só implementação pode ser adequada quando protege uma regra central de um detalhe instável ou permite um teste valioso. Também pode ser ruído se só repete uma chamada sem isolar decisão alguma.

