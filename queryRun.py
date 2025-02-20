import requests
import time
import json
import argparse
import os

# Constantes
DEFAULT_TOKEN_EXPIRATION = 3600  # 1 hora em segundos
DEFAULT_PROPERTIES_FILE = "properties"
DEFAULT_SECRET_FILE = ".secret"

# Função para carregar propriedades do arquivo
def load_properties(properties_file=DEFAULT_PROPERTIES_FILE):
    if not os.path.exists(properties_file):
        raise FileNotFoundError(f"Arquivo de propriedades '{properties_file}' não encontrado.")
    
    with open(properties_file, "r") as file:
        properties = dict(line.strip().split("=", 1) for line in file if "=" in line)
    
    token_endpoint = properties.get("TOKEN_ENDPOINT")
    query_endpoint = properties.get("QUERY_ENDPOINT")
    
    if not token_endpoint or not query_endpoint:
        raise ValueError(f"Arquivo de propriedades '{properties_file}' está incompleto ou mal formatado.")
    
    return token_endpoint, query_endpoint

# Função para carregar credenciais do arquivo .secret
def load_credentials(secret_file=DEFAULT_SECRET_FILE):
    if not os.path.exists(secret_file):
        raise FileNotFoundError(f"Arquivo de credenciais '{secret_file}' não encontrado.")
    
    with open(secret_file, "r") as file:
        credentials = dict(line.strip().split("=", 1) for line in file if "=" in line)
    
    username = credentials.get("USERNAME")
    password = credentials.get("PASSWORD")
    
    if not username or not password:
        raise ValueError(f"Arquivo de credenciais '{secret_file}' está incompleto ou mal formatado.")
    
    return username, password

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
        token_data["expires_at"] = time.time() + data["auth_token"].get("expires_in", DEFAULT_TOKEN_EXPIRATION)
        
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
    parser.add_argument("--properties", type=str, default=DEFAULT_PROPERTIES_FILE, help="Caminho para o arquivo de propriedades")
    parser.add_argument("--secret", type=str, default=DEFAULT_SECRET_FILE, help="Caminho para o arquivo de credenciais")
    args = parser.parse_args()
    
    try:
        TOKEN_ENDPOINT, QUERY_ENDPOINT = load_properties(args.properties)
        USERNAME, PASSWORD = load_credentials(args.secret)
    except (FileNotFoundError, ValueError) as e:
        print(f"Erro ao carregar configurações: {e}")
        exit(1)
    
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