---
arquivo_id: "f6-27-4-03-segredos-csp-dependencias-01-teoria-md"
parent_key: "27.4"
tipo_arquivo: "theory"
assunto: "03_segredos_csp_dependencias"
ordem: 3
itens_origem: ["### 4. Manter segredos e dependências fora do bundle"]
---

### 4. Manter segredos e dependências fora do bundle
Tudo que é incluído no bundle e enviado ao navegador deve ser considerado público: nomes de variáveis “públicas”, chaves de análise, configurações e mapas de fonte podem aparecer no código entregue. Segredos de servidor — chaves privadas, senhas, tokens e credenciais de banco — ficam no backend ou em serviço apropriado, nunca em variáveis destinadas ao cliente. Uma chave deliberadamente pública ainda pode exigir restrição de origem, escopo, quota e monitoramento.

Revise dependências, lockfile, origem/nome dos pacotes e scripts de instalação segundo o fluxo adotado pelo projeto. `npm audit` compara dependências a avisos conhecidos e pode apontar correções; resultado limpo não prova segurança, e atualização automática sem revisão pode quebrar compatibilidade. Registre o achado, versão afetada, risco para o uso real e correção validada.

