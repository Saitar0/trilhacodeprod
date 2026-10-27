---
arquivo_id: "f4-16-3-01-projeto-trilho-b-c04-aceite-04"
parent_key: "16.3"
tipo_arquivo: "checklist"
assunto: "01_projeto_trilho_b"
ordem: 4
itens_origem: ["M4"]
titulo_marco: "Marco 4 — Provar a regra difícil e fechar a entrega"
---

**Aceite por tipo:**
- **T1:** duas tentativas concorrentes para o último ingresso não podem produzir estoque vendido acima do disponível; mostre as transações/resultado final.
- **T2:** consultas com tenant A não retornam dados de B; duas reservas incompatíveis para o mesmo recurso e intervalo são impedidas pela regra do banco, quando esse é o modelo escolhido.
- **T4:** filtros e ordenação retornam páginas corretas e estáveis; consulta medida e cache demonstram miss/hit/invalidação sem usar o cache como fonte de verdade.
- **T5:** carga inclui linhas válidas e inválidas; registros rejeitados são contabilizados com motivo; a agregação bate com os dados aceitos e o procedimento de carga é documentado. Idempotência avançada e processamento por fila pertencem a fases posteriores, salvo se forem necessários ao escopo escolhido.

