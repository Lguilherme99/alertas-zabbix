import requests
import json
import warnings
from datetime import datetime, timedelta

# Desabilitar aviso de SSL
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Configurações da API do Zabbix
ZABBIX_URL = "https://glmonitoria.ddns.net/zabbix/api_jsonrpc.php"
ZABBIX_USER = "luiz.lima"
ZABBIX_PASSWORD = "Sucesso.10!"
OUTPUT_FILE = "/opt/API/Historico_alertas.txt"

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

# Função para buscar eventos com severidade "High" e "Disaster" e status RESOLVED nos últimos 7 dias
def get_resolved_events(auth_token):
    # Calcular o timestamp de 7 dias atrás
    seven_days_ago = datetime.now() - timedelta(days=7)
    time_from = int(seven_days_ago.timestamp())

    # Ajustando a consulta para buscar eventos RESOLVED (value=0)
    events_payload = {
        "jsonrpc": "2.0",
        "method": "event.get",
        "params": {
            "output": ["eventid", "clock", "severity", "acknowledged", "name", "value"],
            "selectHosts": ["host", "hostid"],
            "sortfield": "clock",
            "sortorder": "DESC",
            "time_from": time_from,  # Filtro de tempo para os últimos 7 dias
            "filter": {
                "value": "1"  # Apenas eventos RESOLVED
            }
        },
        "auth": auth_token,
        "id": 2
    }

    response = requests.post(ZABBIX_URL, headers=HEADERS, data=json.dumps(events_payload), verify=False)
    response_json = response.json()
    if "result" in response_json:
        # Filtrar eventos com severidade High (4) e Disaster (5)
        resolved_events = [
            event for event in response_json["result"] if event["severity"] in ["4", "5"]
        ]
        return resolved_events
    else:
        raise Exception(f"Erro ao buscar eventos: {response_json.get('error', 'Erro desconhecido')}")

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

# Função para salvar os eventos em um arquivo .txt
def save_events_to_file(events, auth_token):
    with open(OUTPUT_FILE, "w") as file:
        # Adicionar texto inicial no arquivo
        file.write("Informações abaixo são de Histórico de alertas já RESOLVIDOS.\n\n")
        
        for event in events:
            timestamp = datetime.fromtimestamp(int(event["clock"])).strftime("%Y-%m-%d %H:%M:%S")
            severity = {
                "0": "Not classified",
                "1": "Information",
                "2": "Warning",
                "3": "Average",
                "4": "High",
                "5": "Disaster"
            }.get(str(event["severity"]), "Unknown")

            status = "RESOLVED"

            host = event["hosts"][0]["host"] if event["hosts"] else "No host"

            # Remover "Off-line" do nome do evento, se existir
            event_name = event.get("name", "No name provided").replace("Off-line", "").strip()

            host_id = event["hosts"][0]["hostid"] if event["hosts"] else None

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

            # Linha com nome do erro, IP e DNS incluídos
            line = f"{timestamp} | Host: {host} | Severity: {severity} | Status: {status} | Event ID: {event['eventid']} | Name: {event_name} | IP: {ip_address} | DNS: {dns_name}\n"
            file.write(line)
    print(f"Eventos salvos com sucesso em {OUTPUT_FILE}")

# Função principal
def main():
    try:
        print("Autenticando na API do Zabbix...")
        auth_token = zabbix_login()
        print("Login bem-sucedido!")

        print("Buscando eventos RESOLVED nos últimos 7 dias...")
        events = get_resolved_events(auth_token)
        print(f"{len(events)} eventos encontrados.")

        print("Salvando eventos no arquivo...")
        save_events_to_file(events, auth_token)

    except Exception as e:
        print(f"Erro: {e}")

# Executa o script
if __name__ == "__main__":
    main()
