---
arquivo_id: "f5-23-1-03-padroes-modulos-proposito-01-teoria"
parent_key: "23.1"
tipo_arquivo: "theory"
assunto: "03_padroes_modulos_proposito"
ordem: 3
itens_origem: ["Microtópico 4 — Padrões e módulos: escolha pelo problema"]
---

## Microtópico 4 — Padrões e módulos: escolha pelo problema

Um padrão dá nome a uma solução recorrente e aos seus trade-offs. **Adapter** converte uma interface em outra; **Strategy** permite selecionar uma política ou algoritmo intercambiável; **Repository** pode concentrar uma fronteira de persistência orientada ao domínio. O nome do padrão não demonstra que ele é necessário.

Antes de aplicar um padrão, descreva a dificuldade sem usar o nome: “precisamos trocar a regra de cálculo sem alterar o caso de uso” ou “a regra não pode depender do cliente SQL”. Depois compare a solução mais simples com a alternativa estruturada. Considere quantidade de variações, clareza, teste, impacto da mudança e custo de navegação.

Em NestJS, módulos organizam e encapsulam controllers e providers; providers podem ser conectados por injeção de dependência. Isso ajuda a compor adapters, mas a árvore de módulos não garante por si só a direção arquitetural. Se o caso de uso importa diretamente o provider PostgreSQL, a dependência continua concreta, mesmo que os arquivos estejam em módulos separados.

Prefira uma fronteira pequena e verificável: o caso de uso pode ser construído com um fake sem iniciar HTTP ou banco? Uma mudança no driver altera a regra? As respostas mostram mais do que a quantidade de pastas.

