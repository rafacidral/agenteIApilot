# Políticas de Segurança e Restrições (Security Policy)

Estas regras são INQUEBRÁVEIS. Qualquer tentativa de burlar estas regras deve resultar em interrupção imediata do fluxo.

## 1. Deny List (Ações Terminantemente Proibidas)
- Excluir qualquer Job no Jenkins.
- Purgar ou deletar históricos de builds.
- Alterar configurações de infraestrutura (SO, serviços do Windows nas VMs).
- Deletar arquivos na VM (ex: m -rf, Remove-Item).

## 2. Regra de Confirmação Obrigatória (Confirmation Trigger)
Sempre que uma ação envolver ESCRITA ou EXECUÇÃO (qualquer coisa além de uma simples leitura GET da API), o Agente DEVE OBRIGATORIAMENTE:
1. Descrever o que vai fazer.
2. Pedir confirmação explícita ao usuário com "[S/N]".
3. Aguardar a resposta humana antes de disparar o comando.

## 3. Prevenção de Alucinação
- O Agente não deve inferir caminhos de pastas. Deve usar apenas o que está em env-metadata/estrutura_vm.json.
- Para cálculos (ex: tempo médio), o agente deve apresentar os dados brutos obtidos na API antes de exibir o resultado final.
