---
arquivo_id: "f5-23-1-01-fronteiras-e-ports-adapters-01-teoria"
parent_key: "23.1"
tipo_arquivo: "theory"
assunto: "01_fronteiras_e_ports_adapters"
ordem: 1
itens_origem: ["theory-container", "Microtópico 1 — Arquitetura começa por uma decisão de mudança", "Microtópico 2 — Ports and adapters protege uma conversa"]
---

## Teoria

## Microtópico 1 — Arquitetura começa por uma decisão de mudança

Arquitetura não é o desenho de pastas nem a escolha de um padrão famoso. Ela aparece nas decisões que tornam mais fácil ou mais caro mudar partes do sistema: regras de negócio, interface, persistência, integrações e operação. Uma boa fronteira reduz o alcance de uma mudança relevante sem exigir camadas que não resolvem um problema real.

Considere uma reserva de sala: a regra não pode confirmar duas reservas sobrepostas. A aplicação também precisa receber uma requisição HTTP, consultar disponibilidade e salvar a reserva. Essas necessidades não têm o mesmo ritmo de mudança. A regra de conflito pode continuar igual mesmo que o sistema troque NestJS, PostgreSQL ou a interface web.

Comece identificando:
- qual regra precisa continuar válida;
- qual detalhe externo pode variar ou é difícil de testar;
- qual dependência direta faz a regra conhecer esse detalhe;
- qual custo a fronteira adicionará em implementação, leitura e manutenção.

Não há obrigação de abstrair todo acesso a dados. Se um detalhe é estável, simples e não atrapalha teste ou mudança, uma abstração pode custar mais do que oferece.

## Microtópico 2 — Ports and adapters protege uma conversa

Em ports and adapters, ou arquitetura hexagonal, uma porta representa uma conversa de que a aplicação precisa ou que oferece. Um adapter converte uma tecnologia externa para essa conversa. O formato do desenho com seis lados não é uma regra de estrutura.

No exemplo, a regra de reserva pode precisar consultar e salvar reservas. A porta pode ser descrita pelo próprio vocabulário da aplicação, por exemplo, “consultar conflito” e “salvar reserva”. Um adapter PostgreSQL traduz isso para consultas SQL; um fake em memória pode oferecer a mesma conversa durante um teste.

O sentido da dependência importa: o caso de uso deve conhecer o contrato que usa; a implementação concreta conhece o banco e se encaixa nesse contrato. A porta não precisa imitar a API do PostgreSQL. Se ela expõe detalhes de SQL, a fronteira não isolou a persistência.

Uma porta também pode estar no lado de entrada. Um controller HTTP adapta uma requisição externa ao comando compreendido pela aplicação. Não confunda a ideia arquitetural com uma interface TypeScript obrigatória: uma porta pode ser expressa por tipos, classes abstratas ou tokens, conforme linguagem e composição.

