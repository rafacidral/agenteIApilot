# 🤖 Agente IA Pilot - Base de Conhecimento e Execução

Este repositório atua como a fonte central de verdade para a infraestrutura do Jenkins, topologia de rede e automações operadas pelo Agente de IA (Antigravity).

## 📂 1. Estrutura de Diretórios e Regras de Armazenamento

O Agente Antigravity e os operadores humanos devem respeitar estritamente a seguinte organização:

* **/scripts**: Exclusivo para códigos executáveis e de automação (`.py`, `.ps1`, `.bat`, `.sh`, `.groovy`). Todo script novo deve ser salvo aqui com o controle de versão em seu cabeçalho.
* **/env-metadata**: Exclusivo para os mapeamentos dinâmicos de infraestrutura (`.json`). Contém os arquivos `estrutura_vm.json`, `estrutura_jenkins.json` e `estrutura_workspace.json`. 
* **/docs**: Exclusivo para documentações, guias de melhores práticas e logs estruturados em formato `.md`.

## ⚙️ 2. Instruções de Operação para o Agente (Antigravity)

Ao receber uma nova tarefa que envolva a infraestrutura, o Agente deve obrigatoriamente:

1. **Sincronizar o Contexto:** Acessar e ler os dados atualizados na pasta `/env-metadata` para identificar caminhos absolutos, disponibilidade de espaço em disco e configuração do Jenkins.
2. **Consultar Exemplos:** Analisar códigos pré-existentes na pasta `/scripts` para manter a padronização e o estilo de codificação.
3. **Não Inferir Caminhos:** É proibido adivinhar diretórios. Se um caminho não estiver no mapeamento do `/env-metadata`, o Agente deve solicitar uma nova varredura ou perguntar ao operador.

## 🔄 3. Regras de Atualização e Reversibilidade (Git)

Para garantir que qualquer alteração feita pelo Agente ou pelo usuário possa ser facilmente revertida em caso de falha, as seguintes regras de versionamento se aplicam:

1. **Commits Atômicos e Isolados:** Cada commit deve conter apenas um escopo de alteração. Não misture a criação de um script com a atualização de um arquivo JSON.
2. **Padrão de Mensagens:** As mensagens de commit devem ser explícitas para facilitar o `git revert`:
   * `feat: [Nome do Script/Job]` -> Adição de novas funcionalidades.
   * `fix: [Descrição do Erro]` -> Correções de scripts existentes (mudança de versão decimal).
   * `docs: atualiza mapeamento de infraestrutura` -> Exclusivo para alterações em `/docs` ou `/env-metadata`.
3. **Preservação do Histórico:** É terminantemente proibido o uso de comandos destrutivos (como `git push --force` ou rebase interativo que altere commits antigos). O histórico deve ser sempre progressivo para garantir a segurança da automação.
