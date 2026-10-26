---
arquivo_id: "f1-2-3-02-chaves-01-teoria"
parent_key: "2.3"
tipo_arquivo: "theory"
assunto: "02_chaves"
ordem: 2
itens_origem: ["Chaves pública e privada"]
---

### Chaves pública e privada
Uma chave SSH é um par criptográfico: **chave privada** e **chave pública**. A privada fica sob controle da pessoa e não deve ser enviada a terceiros, publicada ou adicionada ao Git. A pública pode ser cadastrada no serviço remoto. Durante a autenticação, o cliente demonstra que controla a chave privada associada à chave pública cadastrada.

Uma frase secreta (passphrase) pode proteger a chave privada armazenada. Um agente SSH pode manter a chave desbloqueada durante uma sessão, evitando digitar a frase repetidamente. Proteja o dispositivo e remova chaves que não devem mais ter acesso. A chave SSH não é a mesma coisa que um token de API: são credenciais e fluxos de autenticação diferentes.

