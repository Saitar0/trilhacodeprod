---
arquivo_id: "f7-36-1-02-state-drift-colaboracao-p03-pratica-md"
parent_key: "36.1"
tipo_arquivo: "practice"
assunto: "02_state_drift_colaboracao"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Proteja state e prepare colaboração/limpeza

**Desafio:** escolha armazenamento e fluxo de colaboração apropriados ao estágio do laboratório.

**Passos:**
1. Compare state local individual com backend remoto para equipe; avalie acesso, criptografia, locking, versionamento, recuperação, custo e operação.
2. Consulte a documentação do backend escolhido e registre quais controles ele oferece e quais precisam ser adicionados. Não presuma locking por ser remoto.
3. Liste caminhos sensíveis que devem ser ignorados e os controles para artifacts, logs, backups e credenciais temporárias do CI.
4. Simule em papel uma falha durante gravação de state e uma execução concorrente; explique prevenção/recuperação sem editar manualmente o state.
5. Prepare plano de encerramento: inspecione destroy, preserve dados que precisam ser retidos e confirme estado/custos após limpeza num sandbox autorizado.

**Evidências:** decisão de backend; mapa de acesso e recuperação; `.gitignore`; desenho de concorrência; checklist e evidência de limpeza, se executada.

**Verificação:** o state pode ser recuperado sem exposição pública; runs concorrentes não sobrescrevem o mesmo estado quando backend suporta lock; restauração e remoção consideram dados persistentes.

**Aceite:** trade-offs do backend são explícitos; state e plano são tratados como sensíveis; controles reais do backend foram verificados; plano de limpeza respeita retenção.

