---
arquivo_id: "f5-22-1-01-modulos-grafo-e-composicao-01-teoria"
parent_key: "22.1"
tipo_arquivo: "theory"
assunto: "01_modulos_grafo_e_composicao"
ordem: 1
itens_origem: ["Microtópico 1 — O módulo e o grafo da aplicação", "Microtópico 4 — Fronteiras e composição sem atalhos globais"]
---

## Microtópico 1 — O módulo e o grafo da aplicação
NestJS lê metadados dos módulos para montar o grafo da aplicação e resolver providers. O módulo raiz inicia esse grafo; módulos de feature agrupam controllers e providers ligados a uma capacidade, como pedidos ou catálogo. Um módulo declara controllers, providers, imports e exports.

Por padrão, providers ficam encapsulados no módulo que os registra. Para compartilhar um provider, um módulo consumidor importa o módulo que o exporta. O conjunto exportado é a interface pública do módulo. Isso ajuda a tornar explícito quais capacidades outros módulos podem usar.

**Exemplo:** OrdersModule declara OrdersController e OrdersService. Se BillingModule realmente precisa consultar pedidos, OrdersModule pode exportar um provider adequado; BillingModule importa OrdersModule. Não precisa registrar uma segunda cópia de OrdersService em BillingModule.

**Erro comum:** importar todos os módulos em um módulo global central ou exportar todos os providers de cada feature. Isso reduz a clareza do grafo e cria dependências não intencionais.

**Checagem:** um módulo consumidor consegue indicar qual módulo fornece cada dependência e qual provider foi exportado?

## Microtópico 4 — Fronteiras e composição sem atalhos globais
Organize módulos pela capacidade que eles oferecem e pelas dependências que precisam usar. Exporte apenas o necessário, importe explicitamente a feature proprietária da capacidade e evite duplicar registros de providers que deveriam ser compartilhados. Módulos globais reduzem imports, mas tornam as dependências invisíveis; use globalização somente para um caso transversal bem delimitado e registrado uma vez.

Dependência circular entre módulos ou providers pode indicar responsabilidade compartilhada, dependência invertida ou fronteira mal colocada. Primeiro procure uma direção mais simples: extrair uma capacidade comum, inverter uma dependência por contrato ou reunir comportamento que muda junto. Nest oferece forwardRef e ModuleRef para alguns casos em que o ciclo é inevitável, mas eles não corrigem o desenho por si mesmos.

Módulos dinâmicos são úteis quando a configuração do provider depende de opções fornecidas no momento de importação. Não é necessário usá-los para todo módulo ou configuração estática.

**Exemplo:** AuthModule pode exportar um provider de identidade consumido por módulos que precisam autenticar, enquanto cada módulo mantém suas regras próprias. Um módulo global genérico que exporta todos os serviços dificultaria saber quem depende do quê.

**Erro comum:** usar forwardRef como primeira solução para qualquer erro de injeção, ou converter todo módulo em global para contornar imports ausentes.

**Checagem:** o grafo continua legível sem depender de estado global ou ciclos difíceis de explicar?

