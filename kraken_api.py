import time
import base64
import hashlib
import hmac
import requests
import json

API_KEY = '5BR049jMzfuhNvE22c9MRLOyVa+NlJr3UpXqe5S5Zfa/iHoQU0yy6oHk'  # Reemplaza con tu nueva clave API de Kraken
API_SECRET = 'JayudfYtCGqGlWDVM4uCkJgqSZc0RW0HWmyKfGcjNY//hxF3dAkeFNAzinrwsR8BeWqlv20emCurR8FRQ3Ewxw=='  # Reemplaza con tu nueva clave secreta de Kraken

def generate_nonce():
    return str(int(time.time() * 1000))

def generate_signature(uri_path, data, secret):
    postdata = json.dumps(data, separators=(',', ':'))  # Convertir diccionario a JSON
    encoded = (data['nonce'] + postdata).encode()
    message = uri_path.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

uri_path = '/0/private/AddOrder'
nonce = generate_nonce()
data = {
    'nonce': nonce,
    'ordertype': 'market',
    'type': 'buy',  # o 'sell'
    'volume': '0.0001',  # Ajusta el volumen según sea necesario
    'pair': 'XXBTZUSD'
}

# Generar la firma (API-Sign)
api_sign = generate_signature(uri_path, data, API_SECRET)

print("API-Sign: ", api_sign)