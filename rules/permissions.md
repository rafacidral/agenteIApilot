# Matriz de Permissões - Agente IA Pilot

| Nível | Papel | Permissões (O que PODE) | Restrições (O que NUNCA PODE) |
| :--- | :--- | :--- | :--- |
| **Estagiário (Analista)** | **Data-Driven Info** | **Leitura Total via API**: Status, Logs, Métricas, Tempo de Build, Histórico. Cálculos: Médias e correlações. | **Ação Zero**: Proibido clicar em "Build", "Delete", "Configure" ou alterar a infraestrutura. |
| **Master** | Operador | Tudo do Estagiário + Iniciar/Abortar Pipelines de teste (ex: Oracle/Postgres). | Proibido Deletar Jobs, alterar configurações globais do Jenkins, mexer no SO das VMs. |
| **ADM** | Arquiteto | Tudo do Master + Criar/Deletar Jobs, configurar Plugins, gerenciar credenciais. | Reservado para ação humana ou automação sob supervisão direta. |

*Nota: Atualmente, o Agente IA Pilot opera EXCLUSIVAMENTE no nível Estagiário.*
