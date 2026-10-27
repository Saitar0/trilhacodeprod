---
arquivo_id: "f5-20-2-03-csrf-e-segredos-01-teoria"
parent_key: "20.2"
tipo_arquivo: "theory"
assunto: "03_csrf_e_segredos"
ordem: 3
itens_origem: ["Microtópico 4 — CSRF em credenciais enviadas automaticamente", "Microtópico 5 — Segredos e resposta a exposição"]
---

## Microtópico 4 — CSRF em credenciais enviadas automaticamente
CSRF induz o navegador de uma pessoa autenticada a enviar uma requisição que leva suas credenciais automáticas, como cookies. Proteja operações que alteram estado. Use mecanismos mantidos pelo framework, como token CSRF associado à sessão, validação de origem e, quando compatível com o desenho, Fetch Metadata. SameSite pode reduzir cenários, mas em geral deve ser defesa adicional; só o trate como defesa suficiente quando os pressupostos da aplicação e dos navegadores estiverem conscientemente atendidos.

Use GET e outros métodos seguros apenas para leitura, sem efeitos colaterais. Não confunda CORS com CSRF: política de leitura cross-origin não garante que nenhuma requisição forjada será enviada. Também não trate HttpOnly como solução CSRF: ele limita leitura do cookie por JavaScript, mas não impede o navegador de anexá-lo automaticamente.

**Exemplo:** um formulário cross-site tenta enviar uma alteração usando o cookie de sessão da vítima. O servidor exige a defesa CSRF prevista pela arquitetura e rejeita a operação sem uma prova válida.

**Erro comum:** proteger apenas a interface, esconder o botão ou depender exclusivamente de SameSite sem verificar subdomínios, fluxos e suporte do navegador.

**Checagem:** como a API distingue uma alteração iniciada pelo fluxo legítimo da aplicação de uma requisição forjada que leva o cookie da pessoa?

## Microtópico 5 — Segredos e resposta a exposição
Segredos incluem senhas de serviço, chaves, tokens, certificados e credenciais de banco. Não os inclua em código, histórico Git, imagem de container, artefato de build, captura ou log. Um arquivo .env pode ser útil para desenvolvimento local se estiver ignorado e preenchido com valores descartáveis; não é, por si só, cofre de segredos de produção. Variáveis de ambiente também podem ficar acessíveis a processos ou aparecer em dumps e logs, então a plataforma deve prover e proteger as credenciais de forma deliberada.

Prefira armazenamento e entrega de segredos próprios do ambiente de execução, controle de acesso de menor privilégio, credenciais distintas por ambiente, auditoria e rotação planejada. Se um segredo foi publicado, trate-o como comprometido: revogue ou troque primeiro e atualize todos os consumidores. Apagar o arquivo ou limpar o histórico não invalida a credencial que já vazou. Após conter o incidente, avalie logs, acessos e se é necessário reescrever histórico ou remover cópias expostas.

Rotação periódica não é a mesma coisa que trocar uma senha de usuário sem motivo; siga a política apropriada ao tipo de credencial e ao risco. Uma chave ou segredo de serviço comprometido deve ser revogado e substituído com um plano que mantenha a aplicação funcional sem prolongar o uso do valor antigo.

**Exemplo:** uma chave de API real apareceu em commit. O responsável revoga a chave no provedor, provisiona uma nova pelo mecanismo seguro da plataforma, confirma que os serviços deixaram de usar a antiga e então remove a exposição residual dos repositórios e artefatos.

**Erro comum:** apenas adicionar o arquivo ao .gitignore depois do commit, ou acreditar que apagar a linha elimina cópias, clones e credencial ativa.

**Checagem:** qual é a primeira ação após descobrir um segredo ativo no repositório? Revogá-lo ou substituí-lo pelo serviço emissor e atualizar consumidores; a limpeza do repositório é etapa complementar.

