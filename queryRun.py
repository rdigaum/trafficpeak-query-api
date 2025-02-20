import requests
import time
import json
import argparse

# Função para carregar propriedades de um arquivo
def load_properties(properties_file="properties"):
    with open(properties_file, "r") as file:
        properties = dict(line.strip().split("=", 1) for line in file if "=" in line)
    return properties.get("TOKEN_ENDPOINT"), properties.get("QUERY_ENDPOINT")

# Função para carregar credenciais do arquivo .secret
def load_credentials(secret_file=".secret"):
    with open(secret_file, "r") as file:
        credentials = dict(line.strip().split("=", 1) for line in file if "=" in line)
    return credentials.get("USERNAME"), credentials.get("PASSWORD")

TOKEN_ENDPOINT, QUERY_ENDPOINT = load_properties()
USERNAME, PASSWORD = load_credentials()

# Armazena o token JWT e o tempo de expiração
token_data = {"token": None, "expires_at": 0}

def get_jwt_token():
    """Obtém um novo token JWT se ele estiver expirado ou ausente."""
    global token_data
    
    if token_data["token"] and time.time() < token_data["expires_at"]:
        return token_data["token"]
    
    url = f"https://{TOKEN_ENDPOINT}"
    headers = {"Content-Type": "application/json"}
    payload = {"username": USERNAME, "password": PASSWORD}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "auth_token" not in data or "access_token" not in data["auth_token"]:
            raise KeyError("A resposta da API não contém um access_token válido. Resposta recebida: " + json.dumps(data, indent=4))
        
        token_data["token"] = data["auth_token"]["access_token"]
        token_data["expires_at"] = time.time() + data["auth_token"].get("expires_in", 3600)  # Default: 1 hora
        
        print("Token JWT obtido com sucesso!")
        return token_data["token"]
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição do token: {e}")
        exit(1)
    except KeyError as e:
        print(f"Erro ao obter o token JWT: {e}")
        exit(1)

def query_data(sql_query):
    """Realiza uma consulta na API Hydrolix usando um token JWT válido."""
    token = get_jwt_token()
    
    url = f"https://{QUERY_ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = sql_query  # Envia a query como string direta
    
    try:
        print(f"Enviando query para {url}...")
        print("Payload da requisição:", payload)
        response = requests.post(url, data=payload, headers=headers)
        
        if response.status_code == 400:
            print("Erro 400 - Bad Request: Verifique a sintaxe da query e os parâmetros enviados.")
            print("Resposta da API:", response.text)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao executar a query: {e}")
        exit(1)

# Exemplo de uso
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executar consulta na API Hydrolix")
    parser.add_argument("action", choices=["get_token", "run_query"], help="Escolha entre gerar um token ou executar uma query")
    parser.add_argument("--query", type=str, help="Consulta SQL a ser executada (obrigatória para run_query)")
    args = parser.parse_args()
    
    if args.action == "get_token":
        token = get_jwt_token()
        print("Token JWT:", token)
    elif args.action == "run_query":
        if not args.query:
            print("Erro: A opção --query é obrigatória para rodar uma consulta.")
            exit(1)
        result = query_data(args.query)
        print("Resposta da API:")
        print(json.dumps(result, indent=4))
