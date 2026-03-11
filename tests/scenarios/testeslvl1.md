# Cenários de Teste: Nível 1 - Fundamentos e API do Jenkins

**Objetivo:** Validar se o Agente consegue extrair dados básicos exclusivamente via API do Jenkins e formatar saídas longas em colunas limpas, sem alucinar.

## Regras de Formatação:
Sempre que a resposta contiver múltiplas linhas ou listas (ex: lista de VMs e discos), a IA DEVE formatar a saída em colunas simples separadas por vírgula, sem usar formatação Markdown pesada de tabela.
*Exemplo esperado:* Nome da VM, Espaço Total, Espaço Livre

## Tabela de Solicitações e Expectativas

| Solicitação (Prompt do Usuário) | Expectativa de Resposta (Exemplos Aceitáveis) | API / Fonte Esperada |
| :--- | :--- | :--- |
| Oi, Bom dia. | "Bom dia! Como posso ajudar você hoje?" | Resposta direta (Sem API). |
| Que horas são no servidor? | "No servidor Jenkins são 14:11." | API do Jenkins (Header Date ou timestamp de /api/json). |
| Que dia é hoje no servidor? | "Hoje é dia 11 de Março de 2026 no servidor." | API do Jenkins (Header Date). |
| Qual a versão do Jenkins? | "A versão do Jenkins é a 2.528.3." | API raiz do Jenkins (Header X-Jenkins). |
| Qual o nome da VM master? | "A VM master se chama teste458." | Contexto local ou API de nodes. |
| Quantas VMs possuem o Jenkins? | "Temos um total de 15 VMs configuradas." | API /computer/api/json (Contagem total). |
| Quantas VMs estão online agora? | "No momento, temos 13 VMs online." | API /computer/api/json (Filtro offline == false). |
| Liste o espaço em disco de cada VM. | Formato de colunas: 	este458, 50GB, 2.82GB | API /computer/api/json (Monitor de disco) ou metadados. |
