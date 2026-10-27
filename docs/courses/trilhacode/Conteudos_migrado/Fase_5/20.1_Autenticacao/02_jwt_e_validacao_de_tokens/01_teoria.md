---
arquivo_id: "f5-20-1-02-jwt-e-validacao-de-tokens-01-teoria"
parent_key: "20.1"
tipo_arquivo: "theory"
assunto: "02_jwt_e_validacao_de_tokens"
ordem: 2
itens_origem: ["Microtópico 3 — Tokens, JWT e validação"]
---

## Microtópico 3 — Tokens, JWT e validação
Um token é uma credencial apresentada pelo cliente. JWT é um formato para transportar claims; não é sinônimo de OAuth, de sessão, nem prova automática de que a requisição está autorizada. Um JWT assinado (JWS) protege integridade, mas seu payload normalmente pode ser lido por quem obtiver o token. Um JWT criptografado (JWE) é outro formato e deve ser usado conforme necessidade e protocolo.

O servidor que aceita um token precisa verificar sua assinatura com algoritmo permitido e chave confiável e validar as claims exigidas para aquele uso, como emissor, audiência e expiração. Não aceite um token apenas porque seu JSON decodifica, nem confie em campos de identidade ou papel sem validar a origem e o contrato. ID Token informa autenticação ao cliente OIDC; access token é destinado ao recurso/API indicado. Não troque um pelo outro.

JWTs autocontidos podem reduzir consultas para validar estado, mas dificultam revogação imediata: um token emitido pode continuar válido até expirar, a menos que a arquitetura inclua controle de estado ou mecanismo de revogação. Limite escopo e duração de acordo com a necessidade.

**Exemplo:** uma API valida assinatura e audiência do access token que recebeu para si. Ela não usa um ID Token destinado ao cliente web como substituto automático.

**Erro comum:** considerar JWT “mais seguro” ou “sem estado” por definição, armazenar informação sensível no payload assinado e esquecer como invalidar credenciais roubadas.

**Checagem:** que verificações tornam um token aceitável para esta API específica? No mínimo, assinatura/chave confiável, algoritmo permitido e claims exigidas pelo contrato, incluindo audiência quando aplicável.

