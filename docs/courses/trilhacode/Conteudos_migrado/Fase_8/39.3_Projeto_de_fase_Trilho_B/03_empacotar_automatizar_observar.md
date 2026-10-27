---
arquivo_id: "f8-39-3-03-empacotar-automatizar-observar-md"
parent_key: "39.3"
tipo_arquivo: "project_milestone"
ordem: 3
itens_origem: ["M3"]
titulo_marco: "Entrega 3 — Empacotar, automatizar e observar"
---


### Entrega 3 — Empacotar, automatizar e observar

Crie um Dockerfile reproduzível e uma pipeline que execute verificações, construa a imagem e publique/implante no ambiente de teste previsto. Use uma base confiável e mantenha ferramentas de build fora da imagem final quando houver build multi-stage apropriado. Identifique a imagem por versão/commit para ligar o que está implantado ao código revisado.

Configure credenciais e variáveis por mecanismo seguro do ambiente/CI; não passe segredos por `ARG`/`ENV` de build, nem os inclua em imagem, arquivo versionado, log ou artifact. A pipeline precisa mostrar claramente qual etapa testa, qual gera a imagem, qual implanta e qual verifica a saúde. Use revisão/aprovação para aplicar mudanças de infraestrutura quando o fluxo exigir; artefato de plano Terraform pode conter dados sensíveis e não deve ser commitado.

Implemente logs estruturados sem payload sensível e uma métrica de baixa cardinalidade específica do tipo escolhido:

- **T1:** pedidos por minuto, acompanhados de resultado/erro de reserva ou pagamento simulado.
- **T2:** deploy parametrizado por ambiente, staging e rollback; teste de isolamento entre tenants acompanhado por contador de tentativas cross-tenant negadas, sem incluir `tenant_id` como label.
- **T3:** conexão WebSocket/SSE mantida por proxy e HTTPS; métrica de conexões abertas.
- **T4:** latência por endpoint/rota normalizada, com painel de paginação/filtros relevantes.
- **T5:** logs estruturados e métricas de duração e falhas do job.

Conecte o sinal ao painel/consulta em Grafana/Prometheus ou ferramenta equivalente. Um sinal de disponibilidade de host não substitui a métrica do risco central. Registre o que não foi instrumentado, sampling, retenção, limites de custo e sinais ausentes.

**Evidências:** Dockerfile e configuração da pipeline; execução vinculada ao commit; saída dos gates; imagem versionada; implantação em sandbox/staging; health check; consulta/painel com a métrica do tipo; exemplo de log/traces redigidos.


**Feedback:** “pipeline verde” e “endpoint responde” são evidências necessárias, mas insuficientes. Relacione o sinal ao problema técnico e prove que o ambiente está executando a imagem do commit avaliado.

