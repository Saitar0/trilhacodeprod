---
arquivo_id: "f9-46-2-c03-aceite-consumidor-resiliente-retry-e-dlq"
parent_key: "46.2"
tipo_arquivo: "checklist"
ordem: 3
itens_origem: ["M03"]
titulo_marco: "Entrega 3 — Consumidor resiliente, retry e DLQ"
---


**Critérios de aceite:** evento válido produz um efeito; duplicata não duplica efeito; falha transitória tem número máximo e política de recuperação; falha permanente chega à DLQ; redrive tem procedimento e não esconde a causa original.
