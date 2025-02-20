# TrafficPeak Query via API

## Descrição
TrafficPeak Query via API é um projeto em Python que permite obter um token JWT e executar consultas em uma API utilizando autenticação Bearer. O projeto facilita a extração de logs e dados através da API da Hydrolix.

## Referências da API - Akamai Ttraffic Peak
- [Autenticação e geração de token](https://docs.hydrolix.io/reference/config_v1_login_create)
- [Execução de queries via API](https://docs.hydrolix.io/reference/query-data-post)

## Pré-requisitos
Antes de iniciar, certifique-se de ter o seguinte instalado em seu ambiente:

- Python 3.7 ou superior
- `pip` instalado

## Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/rdigaum/trafficpeak-query-api.git
   cd trafficpeak-query-api
   ```

2. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```

## Configuração
O projeto requer arquivos de configuração para armazenar credenciais e endpoints:

1. **Crie o arquivo `.secret`** e adicione suas credenciais:
   ```ini
   USERNAME=seu-usuario
   PASSWORD=sua-senha
   ```

2. **Crie o arquivo `properties`** e defina os endpoints da API:
   ```ini
   TOKEN_ENDPOINT=hostname.trafficpeak/config/v1/login/
   QUERY_ENDPOINT=hostname.trafficpeak/query
   ```

## Uso
O script suporta duas opções: obter o token JWT ou executar uma consulta na API.

### Gerar apenas o token JWT
Para obter um token JWT válido, execute:
```bash
python queryRun.py get_token
```

### Executar uma query
Para executar uma consulta SQL na API, utilize:
```bash
python queryRun.py run_query --query "SELECT reqTimeSec, reqHost, reqPath, securityRules FROM akamai.logs WHERE reqHost = 'hostname' LIMIT 15 FORMAT JSON"
```

## Estrutura do Projeto
```
trafficpeak-query-api/
│── queryRun.py       # Script principal para autenticação e execução de queries
│── requirements.txt   # Dependências do projeto
│── .gitignore        # Arquivos ignorados pelo Git (credenciais e logs)
│── .secret          # Credenciais (não deve ser enviado ao repositório)
│── properties       # Endpoints da API (não deve ser enviado ao repositório)
│── README.md        # Documentação do projeto
```

## Observações
- Certifique-se de **não** enviar os arquivos `.secret` e `properties` para o repositório, pois eles contêm informações sensíveis.
- Utilize um ambiente virtual (`venv`) para evitar conflitos com pacotes globais do Python:
  ```bash
  python -m venv venv
  source venv/bin/activate  # No Linux/Mac
  venv\Scripts\activate  # No Windows
  pip install -r requirements.txt
  ```

## Contribuição
Sinta-se à vontade para abrir issues e enviar pull requests para melhorias no projeto!

## Licença
Este projeto é distribuído sob a licença MIT.

