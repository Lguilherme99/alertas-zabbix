import requests
import json
from datetime import datetime

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

# Função para buscar eventos de severidade High a Disaster
def get_high_severity_events(auth_token):
    # Define o timestamp inicial para buscar eventos das últimas 24h
    time_from = int((datetime.now().timestamp()) - 24 * 60 * 60)

    # Payload ajustado para buscar eventos
    events_payload = {
        "jsonrpc": "2.0",
        "method": "event.get",
        "params": {
            "output": ["eventid", "clock", "name", "severity", "acknowledged"],  # Inclui o "name" do evento
            "selectHosts": ["host"],
            "sortfield": ["clock"],
            "sortorder": "DESC",
            "time_from": time_from,
            "value": 1,  # Apenas eventos de problema (não resolvidos)
            "filter": {
                "severity": ["3", "4", "5"]  # Severidades High (3), Average (4), Disaster (5)
            }
        },
        "auth": auth_token,
        "id": 2
    }
    response = requests.post(ZABBIX_URL, headers=HEADERS, data=json.dumps(events_payload), verify=False)
    response_json = response.json()
    if "result" in response_json:
        return response_json["result"]
    else:
        raise Exception(f"Erro ao buscar eventos: {response_json.get('error', 'Erro desconhecido')}")

# Função para salvar os eventos em um arquivo .txt
def save_events_to_file(events):
    with open(OUTPUT_FILE, "w") as file:
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
            host = event["hosts"][0]["host"] if event["hosts"] else "No host"
            event_name = event.get("name", "No name provided")  # Nome do evento

            # Linha com nome do erro incluído
            line = f"{timestamp} | Host: {host} | Severity: {severity} | Event ID: {event['eventid']} | Name: {event_name}\n"
            file.write(line)
    print(f"Eventos salvos com sucesso em {OUTPUT_FILE}")

# Função principal
def main():
    try:
        print("Autenticando na API do Zabbix...")
        auth_token = zabbix_login()
        print("Login bem-sucedido!")

        print("Buscando eventos de severidade High a Disaster...")
        events = get_high_severity_events(auth_token)
        print(f"{len(events)} eventos encontrados.")

        print("Salvando eventos no arquivo...")
        save_events_to_file(events)

    except Exception as e:
        print(f"Erro: {e}")

# Executa o script
if __name__ == "__main__":
    main()
