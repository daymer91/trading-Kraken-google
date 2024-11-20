from google.cloud import secretmanager
import krakenex  # Biblioteca para interactuar con Kraken API

def get_secret(secret_name, project_id):
    """
    Recupera un secreto almacenado en Google Secret Manager.
    """
    # Crea el cliente de Secret Manager
    client = secretmanager.SecretManagerServiceClient()

    # Define el nombre completo del secreto
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

    # Accede al secreto
    response = client.access_secret_version(name=secret_path)
    return response.payload.data.decode("UTF-8")

def connect_to_kraken():
    """
    Conecta con la API de Kraken utilizando las claves recuperadas de Secret Manager.
    """
    project_id = "trading-view-kareken"  # ID del proyecto
    secret_name_key = "kraken-api-key"  # Nombre del secreto para la clave de API
    secret_name_secret = "kraken-api-secret"  # Nombre del secreto para el secreto de API

    # Recupera las claves desde Secret Manager
    api_key = get_secret(secret_name_key, project_id)
    api_secret = get_secret(secret_name_secret, project_id)

    # Inicializa la conexión con Kraken API
    kraken = krakenex.API(api_key, api_secret)

    # Realiza una llamada de prueba a la API para verificar la conexión
    try:
        response = kraken.query_private('Balance')
        print("Conexión exitosa con Kraken. Respuesta de Balance:")
        print(response)
    except Exception as e:
        print("Error al conectar con Kraken API:", e)

if __name__ == "__main__":
    connect_to_kraken()
