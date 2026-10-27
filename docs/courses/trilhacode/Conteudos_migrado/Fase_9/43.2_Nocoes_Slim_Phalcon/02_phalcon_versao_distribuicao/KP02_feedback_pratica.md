---
arquivo_id: "f9-43-2-02-phalcon-versao-distribuicao-kp02-feedback-pratica"
parent_key: "43.2"
tipo_arquivo: "answer_key_pratica"
assunto: "02_phalcon_versao_distribuicao"
ordem: 2
itens_origem: ["P02"]
---


**Feedback de referência:** Phalcon 5 requer extensão habilitada compatível com PHP; Phalcon 6 documentado é pacote Composer e não exige extensão Phalcon dedicada. Em ambos, valide versões das dependências/extensões e use runtime PHP ainda suportado. Slim e Laravel também dependem do runtime PHP, mas sua instalação comum passa por Composer.

**Erro comum:** atualizar a versão de dependência sem planejar o runtime, build, configuração e retorno do deploy.

