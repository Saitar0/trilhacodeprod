---
arquivo_id: "f9-41-2-01-beneficio-fronteira-01-teoria"
parent_key: "41.2"
tipo_arquivo: "theory"
assunto: "01_beneficio_fronteira"
ordem: 1
itens_origem: ["parágrafo introdutório de ## Teoria", "### 1. Benefício que justifica a fronteira"]
---


A regra prática é: **não crie um serviço distribuído sem um problema concreto que a autonomia dele resolva e sem capacidade para operá-lo**. “Escalar melhor”, “usar a stack da moda” ou “deixar o código mais organizado” não são justificativas suficientes. A decisão pode ser manter o monólito modular, preparar fronteiras internas e medir, ou extrair uma capacidade específica. É uma hipótese arquitetural que deve poder ser revista.

### 1. Benefício que justifica a fronteira
Microsserviço pode permitir deploy, escala, tecnologia ou ownership independentes. Procure uma necessidade observável:
- uma capacidade tem perfil de carga muito diferente e exige escala independente;
- uma equipe precisa entregar e operar uma área com autonomia real;
- falhas ou requisitos de segurança dessa capacidade precisam de isolamento;
- o ritmo de mudança de um domínio causa espera, regressão ou coordenação repetida no conjunto;
- limites de domínio e contratos já são compreensíveis para quem mantém o sistema.

Transforme cada benefício em sinal mensurável. Exemplo: “separar notificações” é uma solução proposta; “picos de notificações elevam a latência do checkout acima do objetivo em X ocorrências” é uma hipótese verificável. Não atribua valor a um benefício sem identificar quem o usa, qual métrica deve mudar e em quanto tempo será reavaliado.

