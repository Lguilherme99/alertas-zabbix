import requests
import json

# URL do Zabbix API
url = 'https://glmonitoria.ddns.net/zabbix/api_jsonrpc.php'

# Credenciais do Zabbix
user = 'luiz.lima'
password = 'Sucesso.10!'

# Cabeçalhos da requisição
headers = {
    'Content-Type': 'application/json-rpc'
}

# Corpo da requisição de login ajustado
login_data = {
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
        "username": user,  # Use "username" em vez de "user"
        "password": password
    },
    "id": 1
}

# Envia a requisição de login
login_response = requests.post(url, headers=headers, data=json.dumps(login_data))

# Verifica se houve erro no login
login_result = login_response.json()
if 'result' in login_result:
    auth_token = login_result['result']
    print("Login bem-sucedido, token de autenticação:", auth_token)

    # Corpo da requisição para obter a versão da API (sem o auth)
    version_data = {
        "jsonrpc": "2.0",
        "method": "apiinfo.version",  # Método para verificar a versão da API
        "params": {},  # Sem necessidade de auth para este método
        "id": 1
    }

    # Envia a requisição para verificar a versão da API
    version_response = requests.post(url, headers=headers, data=json.dumps(version_data))

    # Exibe a resposta
    result = version_response.json()
    print("Resultado da versão da API:", result)

    # Corpo da requisição para obter informações dos hosts (sem interfaces)
    host_data = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["host"],  # Retorna apenas o nome do host
        },
        "auth": auth_token,  # Passa o token de autenticação
        "id": 2
    }

    # Envia a requisição para obter informações dos hosts
    host_response = requests.post(url, headers=headers, data=json.dumps(host_data))

    # Exibe a resposta
    host_result = host_response.json()
    print("Informações dos hosts:")
    
    if 'result' in host_result:
        if len(host_result['result']) == 0:
            print("Nenhum host encontrado.")
        else:
            for host in host_result['result']:
                print(f"Host: {host['host']}")
    else:
        print("Erro ao obter informações dos hosts:", host_result)
else:
    print("Erro no login:", login_result)
