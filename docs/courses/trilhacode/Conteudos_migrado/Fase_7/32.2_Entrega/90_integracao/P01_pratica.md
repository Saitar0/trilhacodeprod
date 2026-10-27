---
arquivo_id: "f7-32-2-90-integracao-p01-pratica-md"
parent_key: "32.2"
tipo_arquivo: "practice"
assuntos: ["01_identidade_do_artefato", "02_ambientes_autorizacao_promocao"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Produza e promova um artefato

**Desafio:** monte um fluxo que constrói uma aplicação uma vez e disponibiliza a mesma saída em staging.

**Passos:**
1. Identifique o commit de origem, o comando de build e a pasta/imagem produzida.
2. Faça os checks da unidade 32.1 dependerem do build e salve o artefato com nome associado à versão/commit.
3. Configure o job de staging para baixar o artefato da execução correspondente e implantar essa saída sem executar um novo build.
4. Separe configuração e secrets do pacote; use uma conta e dados de staging isolados.
5. Registre commit, nome/digest do artefato, ambiente, horário e resultado da implantação.

**Evidências:** workflow; log de build e deploy; identificação do artefato antes/depois; configuração sem segredos; URL ou registro do ambiente de staging.

**Verificação:** compare a identidade do artefato produzido com a implantada; confirme que o workflow não recompila durante a promoção e que staging não aponta para recursos reais de produção.

**Aceite:** artefato e commit são rastreáveis; a mesma saída chega ao staging; configuração é externa e segura; o processo é reproduzível em uma nova execução.

