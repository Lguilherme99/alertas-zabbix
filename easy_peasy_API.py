import requests
import json

# Configurações da API do Easy Peasy
easy_peasy_url = 'https://bots.easy-peasy.ai/bot/80194440-8e4b-458e-993f-06affbb8598a/api'
api_key = '69f8fe74-db38-4223-8fd9-6629dee974f4'

# Cabeçalhos da API
headers = {
    'Content-Type': 'application/json',
    'x-api-key': api_key
}

def enviar_pergunta(pergunta):
    # Corpo da requisição com a mensagem
    data = {
        "message": pergunta,
        "history": [],
        "stream": False  # Resposta não é em tempo real
    }

    try:
        # Envia a requisição POST para o Easy Peasy
        response = requests.post(easy_peasy_url, headers=headers, data=json.dumps(data))

        # Verifica o status e exibe a resposta
        if response.status_code == 200:
            resposta = response.json()
            return resposta['bot']['text']
        else:
            return f"Erro na API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro ao enviar a requisição: {e}"

# Loop interativo
if __name__ == "__main__":
    print("=== Chat com Easy Peasy ===")
    print("Digite 'sair' para encerrar.\n")

    while True:
        pergunta = input("Você: ").strip()

        # Verifica se o usuário quer sair
        if pergunta.lower() == "sair":
            print("Encerrando o chat. Até mais!")
            break

        # Envia a pergunta para a API e exibe a resposta
        resposta = enviar_pergunta(pergunta)
        print(f"Easy Peasy: {resposta}\n")
