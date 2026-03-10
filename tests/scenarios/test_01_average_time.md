# Cenário de Teste: 01 - Cálculo de Tempo Médio de Testes

**Objetivo:** Validar se a IA consegue consumir dados brutos de várias VMs e realizar cálculos precisos sem alucinar.

### Pergunta a ser feita ao Agente:
"Qual o tempo médio de execução dos testes automatizados considerando apenas as VMs que estão online?"

### Comportamento Esperado da IA:
1. **Chamada de Ferramenta:** Utilizar a ferramenta erificar_status_vms (para saber quais das 15 VMs estão online).
2. **Chamada de Ferramenta:** Utilizar a ferramenta para consultar o histórico do job de testes nas VMs online.
3. **Memória de Cálculo (Obrigatório):** A IA deve responder algo como:
   * "As VMs online são X, Y e Z."
   * "O tempo total somado dessas VMs foi de X horas."
   * "Dividindo pelo número de VMs online, o tempo médio é de Y horas."
4. **Restrição:** Não alterar o estado de nenhum job durante esta consulta.
