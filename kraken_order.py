import time
import hashlib
import hmac
import urllib.parse
import requests

# Datos de autenticación de la API (reemplaza con tus claves)
api_key = '5BR049jMzfuhNvE22c9MRLOyVa+NlJr3UpXqe5S5Zfa/iHoQU0yy6oHk'
api_secret = 'JayudfYtCGqGlWDVM4uCkJgqSZc0RW0HWmyKfGcjNY//hxF3dAkeFNAzinrwsR8BeWqlv20emCurR8FRQ3Ewxw=='

# Endpoint de Kraken para realizar la orden
url = 'https://api.kraken.com/0/private/AddOrder'

# Parámetros de la orden (puedes cambiar el par o la cantidad)
params = {
    'nonce': str(int(time.time() * 1000)),  # Generar un nonce único
    'pair': 'XBTUSD',  # Par de divisas BTC/USD
    'type': 'buy',  # Tipo de orden (compra)
    'ordertype': 'market',  # Orden de mercado
    'volume': '1.0'  # Cantidad a comprar (1 BTC en este caso)
}

# Crear la cadena a firmar
post_data = urllib.parse.urlencode(params)
message = url + post_data

# Firmar la solicitud con la clave privada
signature = hmac.new(
    bytes(api_secret, 'utf-8'),
    message.encode('utf-8'),
    hashlib.sha512
).hexdigest()

# Cabeceras para la solicitud (incluye API-Key y API-Sign)
headers = {
    'API-Key': api_key,
    'API-Sign': signature
}

# Realizar la solicitud POST a Kraken
response = requests.post(url, data=params, headers=headers)

# Mostrar la respuesta de Kraken
print(response.json())
