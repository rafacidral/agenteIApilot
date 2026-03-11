# =============================================================================
# agente_pilot.py
# Versão: v2.0
# Descrição: Loop de chat CLI com padrão Gateway Tool.
#             Uma única ferramenta 'consultar_jenkins' recebe um parâmetro
#             Acao e roteia para o script PowerShell centralizado.
# Uso: python agente_pilot.py
# =============================================================================

import json
import os
import subprocess
import sys

try:
    import requests
except ImportError:
    print("[ERRO] Biblioteca 'requests' não encontrada. Instale com: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# CONFIGURAÇÕES
# ---------------------------------------------------------------------------
OLLAMA_URL  = "http://localhost:11434/api/chat"
MODEL_NAME  = "qwen2.5:3b"
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
README_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
RULES_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules")

# ---------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ---------------------------------------------------------------------------

def load_text_file(path: str) -> str:
    """Lê um arquivo de texto e retorna o seu conteúdo ou uma string de erro."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[AVISO] Arquivo não encontrado: {path}"
    except Exception as e:
        return f"[ERRO ao ler {path}]: {e}"


def load_rules() -> str:
    """Lê todos os arquivos .md da pasta /rules e os concatena."""
    if not os.path.isdir(RULES_DIR):
        return "[AVISO] Pasta /rules não encontrada."
    parts = []
    for fname in sorted(os.listdir(RULES_DIR)):
        if fname.endswith(".md"):
            fpath = os.path.join(RULES_DIR, fname)
            parts.append(f"### {fname}\n{load_text_file(fpath)}")
    return "\n\n".join(parts) if parts else "[AVISO] Nenhum arquivo .md encontrado em /rules."


# Acoes reconhecidas pelo gateway — lista ESTRITA
GATEWAY_ACTIONS = ["status_vms", "versao_jenkins", "falhas_ultima_execucao", "total_jobs"]
GATEWAY_SCRIPT  = "tool_jenkins_gateway.ps1"

# Modelos pequenos tendem a inventar nomes antigos de funcoes.
# Este mapa captura chamadas erradas e silenciosamente as redireciona.
LEGACY_TOOL_REMAP: dict[str, str] = {
    "tool_verificar_status_vms":        "status_vms",
    "verificar_status_vms":             "status_vms",
    "tool_status_vms":                  "status_vms",
    "tool_versao_jenkins":              "versao_jenkins",
    "versao_jenkins":                   "versao_jenkins",
    "tool_falhas_ultima_execucao":      "falhas_ultima_execucao",
    "falhas_ultima_execucao":           "falhas_ultima_execucao",
}

# Limite de chamadas de ferramenta por turno — evita o loop de ansiedade
MAX_TOOL_CALLS_PER_TURN = 2


def get_gateway_tool_definition() -> list[dict]:
    """
    Retorna a definição de UMA única ferramenta ('consultar_jenkins').
    O modelo só pode escolher entre as Acoes listadas em GATEWAY_ACTIONS.
    Qualquer valor fora da lista resulta em erro estruturado do gateway.
    """
    acoes_str = " | ".join(GATEWAY_ACTIONS)
    return [
        {
            "type": "function",
            "function": {
                "name": "consultar_jenkins",
                "description": (
                    "Consulta o servidor Jenkins (teste458:9090) via gateway centralizado. "
                    "Você DEVE passar o parâmetro 'Acao' com EXATAMENTE um dos valores "
                    f"permitidos: {acoes_str}. "
                    "NÃO invente outros valores de Acao. Se a pergunta do usuário não se "
                    "encaixar em nenhuma dessas ações, NÃO chame esta ferramenta — "
                    "responda ao usuário dizendo que não possui essa informação."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "Acao": {
                            "type": "string",
                            "enum": GATEWAY_ACTIONS,
                            "description": (
                                "Ação a executar no Jenkins. "
                                f"Valores aceitos: {acoes_str}."
                            )
                        }
                    },
                    "required": ["Acao"]
                }
            }
        }
    ]


def run_ps_script(script_filename: str) -> str:
    """
    Executa um script PowerShell em /scripts e retorna o stdout capturado.
    Nunca executa scripts fora de SCRIPTS_DIR (proteção de path traversal).
    """
    safe_name = os.path.basename(script_filename)
    script_path = os.path.join(SCRIPTS_DIR, safe_name)

    if not os.path.isfile(script_path):
        return json.dumps({"erro": f"Script não encontrado: {safe_name}"})

    try:
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
            capture_output=True,
            text=True,
            encoding="cp1252",
            timeout=60
        )
        output = result.stdout.strip() or "(sem saída)"
        if result.returncode != 0:
            output += f"\n[STDERR]: {result.stderr.strip()}"
        return output
    except subprocess.TimeoutExpired:
        return json.dumps({"erro": "Timeout ao executar o script (>60s)."})
    except Exception as e:
        return json.dumps({"erro": f"Falha ao executar script: {e}"})


def dispatch_tool_call(tool_name: str, args: dict) -> str:
    """
    Roteia a chamada para o gateway .ps1 via -Acao.
    Aceita o nome canonico 'consultar_jenkins' ou qualquer apelido em LEGACY_TOOL_REMAP.
    Modelos pequenos tendem a inventar nomes antigos — o remap absorve isso silenciosamente.
    """
    # 1. Normaliza nomes legados
    if tool_name != "consultar_jenkins":
        acao_remapeada = LEGACY_TOOL_REMAP.get(tool_name)
        if not acao_remapeada:
            return json.dumps({
                "erro": (
                    f"Ferramenta '{tool_name}' nao existe. "
                    f"Use APENAS: consultar_jenkins com Acao em {GATEWAY_ACTIONS}."
                )
            })
        # Injeta a acao remapeada nos args e continua normalmente
        args = {"Acao": acao_remapeada}

    # 2. Extrai Acao (pode ter vindo de args originais ou do remap acima)
    acao = args.get("Acao", "").strip()
    if not acao:
        return json.dumps({"erro": "Parametro 'Acao' ausente ou vazio."})

    # 3. Validacao dupla — gateway tambem bloqueia, mas defesa em profundidade
    if acao not in GATEWAY_ACTIONS:
        return json.dumps({
            "erro": f"Acao '{acao}' nao reconhecida. Use: {', '.join(GATEWAY_ACTIONS)}."
        })

    script_path = os.path.join(SCRIPTS_DIR, GATEWAY_SCRIPT)
    if not os.path.isfile(script_path):
        return json.dumps({"erro": f"Script gateway nao encontrado: {GATEWAY_SCRIPT}"})

    try:
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass",
             "-File", script_path, "-Acao", acao],
            capture_output=True,
            text=True,
            encoding="cp1252",
            timeout=60
        )
        output = result.stdout.strip() or "(sem saida)"
        if result.returncode != 0:
            output += f"\n[STDERR]: {result.stderr.strip()}"
        return output
    except subprocess.TimeoutExpired:
        return json.dumps({"erro": "Timeout ao executar o gateway (>60s)."})
    except Exception as e:
        return json.dumps({"erro": f"Falha ao executar gateway: {e}"})


def build_system_prompt() -> str:
    """Monta o prompt de sistema com README + regras de segurança + regras de ferramenta."""
    readme    = load_text_file(README_PATH)
    rules     = load_rules()
    acoes_str = ", ".join(GATEWAY_ACTIONS)

    return f"""Voce e o Agente IA Pilot, um Analista de Dados especialista na infraestrutura
Jenkins da equipe de QA. Opere EXCLUSIVAMENTE no nivel 'Estagiario':
- LEITURA e CALCULO via API sao permitidos.
- Nenhuma escrita, execucao de builds, delecao de jobs ou alteracao de configs.
- Para calculos, apresente SEMPRE os dados brutos e a memoria de calculo antes
  do resultado final (Prevencao de Alucinacao).
- Nao invente caminhos de pastas. Use apenas o que esta em /env-metadata.
- Responda SEMPRE em portugues (pt-BR).
- SEJA CONCISO: va direto ao ponto. Sem frases de enrolacao, sem sugestoes
  nao pedidas, sem repetir o que o usuario ja sabe. Maximo 5 linhas por resposta
  a menos que o usuario peca mais detalhes.

=== REGRA CRITICA DE USO DA FERRAMENTA ===
Voce possui UMA UNICA ferramenta: `consultar_jenkins`.
Ela aceita APENAS os seguintes valores para o campo Acao:
  {acoes_str}

REGRAS OBRIGATORIAS:
1. Para perguntas sobre VMs/nodes ou calculos envolvendo VMs (ex: VMs online, tempo medio, tempo de execucao nas vms) -> Acao=status_vms
2. Para perguntas sobre versao do Jenkins -> Acao=versao_jenkins
3. Para perguntas sobre falhas/resultado do ultimo build -> Acao=falhas_ultima_execucao
4. Para perguntas sobre "quantidade total de jobs" ou similares -> Acao=total_jobs
   NUNCA use status_vms para contar jobs.
5. Para qualquer outra coisa nao mapeada acima, NAO chame a ferramenta. Responda:
   "Chefe, nao tenho comando para isso."
6. NUNCA invente um nome de ferramenta diferente de `consultar_jenkins`.
7. NUNCA chame a ferramenta mais de uma vez por turno.

=== README / Contexto do Projeto ===
{readme}

=== Regras de Seguranca ===
{rules}
"""


def chat_with_ollama(messages: list, tools: list) -> dict:
    """
    Envia a conversa para o Ollama e retorna o JSON completo da resposta.
    Usa streaming=False para simplificar o parsing.
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "tools": tools,
        "stream": False
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Não foi possível conectar ao Ollama. Verifique se ele está rodando em localhost:11434."}
    except requests.exceptions.Timeout:
        return {"error": "Timeout: o Ollama demorou mais de 120 s para responder."}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# LOOP PRINCIPAL
# ---------------------------------------------------------------------------

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 65)
    print("  🤖  Agente IA Pilot  |  Ollama:", MODEL_NAME)
    print("  Modo: Estagiário (Analista) — apenas LEITURA e CÁLCULO")
    print("  Digite 'sair' ou 'exit' para encerrar.")
    print("=" * 65)
    print()

    system_prompt = build_system_prompt()
    tools         = get_gateway_tool_definition()
    messages      = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n[Encerrando o Agente IA Pilot. Até logo!]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("sair", "exit", "quit"):
            print("\n[Encerrando o Agente IA Pilot. Até logo!]")
            break

        messages.append({"role": "user", "content": user_input})

        # --- turno do modelo (com possivel tool-call) ---
        tool_calls_this_turn = 0
        while True:
            response = chat_with_ollama(messages, tools)

            # Erro de conexao / API
            if "error" in response:
                print(f"\n[ERRO]: {response['error']}")
                messages.pop()  # remove a mensagem do usuario que falhou
                break

            msg = response.get("message", {})
            role       = msg.get("role", "assistant")
            content    = msg.get("content", "")
            tool_calls = msg.get("tool_calls", [])

            # Registra a resposta do modelo no historico
            messages.append({"role": role, "content": content, "tool_calls": tool_calls})

            # Se ha chamadas de ferramenta, executa-as e volta ao modelo
            if tool_calls:
                # Guardiao anti-ansiedade: maximo de chamadas por turno
                if tool_calls_this_turn >= MAX_TOOL_CALLS_PER_TURN:
                    print("[AVISO] Limite de chamadas de ferramenta atingido neste turno. Encerrando.")
                    break

                for tc in tool_calls:
                    fn_name = tc.get("function", {}).get("name", "")
                    fn_args = tc.get("function", {}).get("arguments", {})
                    if isinstance(fn_args, str):
                        try:
                            fn_args = json.loads(fn_args)
                        except Exception:
                            fn_args = {}

                    # Mostra qual acao sera executada de forma legivel
                    acao_display = fn_args.get("Acao") or LEGACY_TOOL_REMAP.get(fn_name, fn_name)
                    print(f"[gateway → {acao_display}]")
                    tool_output = dispatch_tool_call(fn_name, fn_args)

                    messages.append({
                        "role": "tool",
                        "name": "consultar_jenkins",   # sempre o nome canonico
                        "content": tool_output
                    })
                    tool_calls_this_turn += 1

                # Volta ao topo do while para o modelo processar os resultados
                continue

            # Resposta final de texto
            # Limpa explicacoes em bloco de pensamento do qwen se houver
            final_text = content or "(sem resposta)"
            if "<|im_start|>thought" in final_text:
                final_text = final_text.split("<|im_end|>")[-1].strip()
            
            print(f"\nAgente: {final_text}\n")
            break   # sai do loop de tool-calls e pede novo input do usuario


if __name__ == "__main__":
    main()
