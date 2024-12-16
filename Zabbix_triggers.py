import requests
import json
import warnings
from datetime import datetime

# Desabilitar aviso de SSL
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Configurações da API do Zabbix
ZABBIX_URL = "https://glmonitoria.ddns.net/zabbix/api_jsonrpc.php"
ZABBIX_USER = "luiz.lima"
ZABBIX_PASSWORD = "Sucesso.10!"
OUTPUT_FILE = "/opt/API/Historico_triggers.txt"

# Cabeçalhos da requisição
HEADERS = {
    "Content-Type": "application/json-rpc"
}

# Função para autenticar no Zabbix
def zabbix_login():
    login_payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": ZABBIX_USER,
            "password": ZABBIX_PASSWORD
        },
        "id": 1
    }
    response = requests.post(ZABBIX_URL, headers=HEADERS, data=json.dumps(login_payload), verify=False)
    response_json = response.json()
    if "result" in response_json:
        return response_json["result"]
    else:
        raise Exception(f"Erro na autenticação: {response_json.get('error', 'Erro desconhecido')}")

# Função para buscar triggers alarmadas (High e Disaster)
def get_trigger_problems(auth_token):
    triggers_payload = {
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "output": ["triggerid", "description", "priority", "value", "lastchange"],  # Infos necessárias
            "selectHosts": ["host", "hostid"],
            "filter": {
                "value": 1  # Apenas triggers em "PROBLEM" (1)
            },
            "sortfield": "lastchange",
            "sortorder": "DESC",
            "min_severity": 4  # Severidade mínima: High (4) e Disaster (5)
        },
        "auth": auth_token,
        "id": 2
    }

    response = requests.post(ZABBIX_URL, headers=HEADERS, data=json.dumps(triggers_payload), verify=False)
    response_json = response.json()
    if "result" in response_json:
        return response_json["result"]
    else:
        raise Exception(f"Erro ao buscar triggers: {response_json.get('error', 'Erro desconhecido')}")

# Função para buscar as interfaces (IP e DNS) de um host
def get_host_interfaces(auth_token, host_id):
    interfaces_payload = {
        "jsonrpc": "2.0",
        "method": "hostinterface.get",
        "params": {
            "output": ["ip", "dns"],
            "hostids": host_id
        },
        "auth": auth_token,
        "id": 3
    }

    response = requests.post(ZABBIX_URL, headers=HEADERS, data=json.dumps(interfaces_payload), verify=False)
    response_json = response.json()
    if "result" in response_json:
        return response_json["result"]
    else:
        return []

# Função para salvar as triggers em um arquivo .txt
def save_triggers_to_file(triggers, auth_token):
    with open(OUTPUT_FILE, "w") as file:
        # Adicionar texto inicial no arquivo
        file.write("Equipamentos Off-line atualmente:\n\n")
        
        for trigger in triggers:
            timestamp = datetime.fromtimestamp(int(trigger["lastchange"])).strftime("%Y-%m-%d %H:%M:%S")
            severity = {
                "0": "Not classified",
                "1": "Information",
                "2": "Warning",
                "3": "Average",
                "4": "High",
                "5": "Disaster"
            }.get(str(trigger["priority"]), "Unknown")

            status = "PROBLEM" if trigger["value"] == "1" else "OK"
            event_name = trigger.get("description", "No description provided")
            host = trigger["hosts"][0]["host"] if trigger["hosts"] else "No host"
            host_id = trigger["hosts"][0]["hostid"] if trigger["hosts"] else None

            ip_address = "No IP"
            dns_name = "No DNS"

            # Se o host tiver um ID, busca as interfaces para obter IP e DNS
            if host_id:
                interfaces = get_host_interfaces(auth_token, host_id)
                for interface in interfaces:
                    if "ip" in interface:
                        ip_address = interface["ip"]
                    if "dns" in interface:
                        dns_name = interface["dns"]

            # Linha com informações da trigger
            line = f"{timestamp} | Host: {host} | Severity: {severity} | Status: {status} | Trigger ID: {trigger['triggerid']} | Name: {event_name} | IP: {ip_address} | DNS: {dns_name}\n"
            file.write(line)
    print(f"Triggers salvas com sucesso em {OUTPUT_FILE}")

# Função principal
def main():
    try:
        print("Autenticando na API do Zabbix...")
        auth_token = zabbix_login()
        print("Login bem-sucedido!")

        print("Buscando todas as triggers alarmadas (High e Disaster)...")
        triggers = get_trigger_problems(auth_token)
        print(f"{len(triggers)} triggers encontradas.")

        print("Salvando triggers no arquivo...")
        save_triggers_to_file(triggers, auth_token)

    except Exception as e:
        print(f"Erro: {e}")

# Executa o script
if __name__ == "__main__":
    main()
