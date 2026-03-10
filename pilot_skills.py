# Versão: v1.0
# Descrição: Definição de Skills (Ferramentas) para o Agente IA Pilot no Antigravity.
# Integra o script PowerShell de monitorização de VMs do Jenkins.

import subprocess
import json
import os

class PilotSkills:
    def __init__(self):
        # Caminho absoluto para a pasta de scripts conforme o README.md
        self.scripts_path = os.path.join(os.getcwd(), "scripts")

    def verificar_status_vms(self):
        """
        Consulta a API do Jenkins no mestre teste458 para obter o status em tempo real 
        de todas as VMs (nós/slaves) da infraestrutura. 
        Retorna se as máquinas estão ONLINE/OFFLINE e LIVRE/OCUPADO.
        """
        script_file = os.path.join(self.scripts_path, "tool_verificar_status_vms.ps1")
        
        try:
            # Executa o PowerShell de forma segura
            process = subprocess.run(
                ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_file],
                capture_output=True,
                text=True,
                encoding='cp1252' # Garante a leitura correta de caracteres do Windows
            )
            
            # Captura apenas a linha do JSON que o nosso script gera no final
            output = process.stdout
            if "RESULTADO_JSON_PARA_IA:" in output:
                json_part = output.split("RESULTADO_JSON_PARA_IA:")[1].strip()
                return json_part
            else:
                return json.dumps({"erro": "O script não retornou um JSON válido. Verifique a execução manual."})
                
        except Exception as e:
            return json.dumps({"erro": f"Falha ao executar a ferramenta: {str(e)}"})

# Esta estrutura é o que o Antigravity envia para o Ollama (Tool Definition)
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "verificar_status_vms",
            "description": "Consulta o Jenkins para saber quais VMs de vwt001mhc001 até 015 estão online e disponíveis.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]
