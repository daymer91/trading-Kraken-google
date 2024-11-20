 import boto3
import json

# Crear un cliente de Secrets Manager
client = boto3.client('secretsmanagertrading-view-kareken', region_name='europe-southwest1')

# Definir el nombre del secreto y las credenciales
secret_name = 'MiSecretoDeBaseDeDatos'
secret_value = {
    "username": "trading-view-kareken",
    "password": "#Arte1991jj"
}

# Crear el secreto
response = client.create_secret(
    Name=secret_name,
    SecretString=json.dumps(secret_value),
    Description='Credenciales para mi base de datos'
)

print(f"Secreto creado con ARN: {response['ARN']}")
