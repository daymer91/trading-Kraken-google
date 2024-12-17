import os
import time
import hmac
import hashlib
import base64
import urllib.parse

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ------------------------------------------------------------------------------
# Configuración: Cargar tus credenciales de Kraken desde variables de entorno
# ------------------------------------------------------------------------------
KRAKEN_API_KEY = os.getenv('KRAKEN_API_KEY', 'TU_API_KEY_PUBLICA')
KRAKEN_API_SECRET = os.getenv('KRAKEN_API_SECRET', 'TU_API_KEY_PRIVADA_BASE64')

# Endpoint base de Kraken y ruta para AddOrder
KRAKEN_API_BASE_URL = "https://api.kraken.com"
KRAKEN_ADD_ORDER_PATH = "/0/private/AddOrder"
KRAKEN_ADD_ORDER_URL = KRAKEN_API_BASE_URL + KRAKEN_ADD_ORDER_PATH


def kraken_signature(url_path: str, data: dict, secret: str) -> str:
    """
    Genera la firma HMAC-SHA512 para Kraken (API-Sign).
    Documentación oficial: https://docs.kraken.com/rest/#section/Authentication
    """
    # 1. Combine nonce + POST data
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode('utf-8')
    
    # 2. SHA256 del string anterior
    message = url_path.encode('utf-8') + hashlib.sha256(encoded).digest()
    
    # 3. Decodificar la secret key desde base64
    secret_decoded = base64.b64decode(secret)
    
    # 4. Generar la firma HMAC-SHA512
    mac = hmac.new(secret_decoded, message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


@app.route('/place_order', methods=['POST'])
def place_order():
    """
    Endpoint Flask que recibe parámetros de la orden y la envía al endpoint AddOrder de Kraken.
    """
    # ------------------------------------------------------------------------------
    # 1. Recibir datos del cliente o de la lógica interna
    # ------------------------------------------------------------------------------
    req_data = request.json
    if not req_data:
        return jsonify({"error": "Falta cuerpo JSON con parámetros de orden"}), 400

    pair = req_data.get("pair", "XBTUSD")
    ordertype = req_data.get("ordertype", "limit")
    order_side = req_data.get("type", "buy")  # 'buy' o 'sell'
    price = req_data.get("price", "37500")
    volume = req_data.get("volume", "1.0")

    # ------------------------------------------------------------------------------
    # 2. Construir payload para Kraken (necesario para AddOrder)
    # ------------------------------------------------------------------------------
    nonce = str(int(time.time() * 1000))  # nonce en milisegundos
    
    payload = {
        "nonce": nonce,
        "ordertype": ordertype,
        "type": order_side,
        "pair": pair,
        "volume": volume
        # Puedes añadir flags opcionales como "validate": "true" para probar
    }

    # Si la orden es de tipo limit, stop-loss-limit, take-profit-limit, etc. agregamos "price"
    if ordertype in ["limit", "stop-loss-limit", "take-profit-limit", "trailing-stop-limit", "iceberg"]:
        payload["price"] = price

    # ------------------------------------------------------------------------------
    # 3. Generar firma (API-Sign)
    # ------------------------------------------------------------------------------
    api_sign = kraken_signature(KRAKEN_ADD_ORDER_PATH, payload, KRAKEN_API_SECRET)

    # ------------------------------------------------------------------------------
    # 4. Configurar encabezados e enviar la petición POST
    # ------------------------------------------------------------------------------
    headers = {
        "API-Key": KRAKEN_API_KEY,
        "API-Sign": api_sign,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    encoded_payload = urllib.parse.urlencode(payload)

    try:
        response = requests.post(KRAKEN_ADD_ORDER_URL, headers=headers, data=encoded_payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"HTTP error: {str(e)}", "detail": response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request error: {str(e)}"}), 500

    # ------------------------------------------------------------------------------
    # 5. Interpretar la respuesta de Kraken
    # ------------------------------------------------------------------------------
    kraken_json = response.json()
    
    if kraken_json.get("error"):
        # Si hay errores de Kraken, normalmente vienen en la lista "error".
        return jsonify({
            "error": kraken_json["error"],
            "result": kraken_json.get("result", {})
        }), 400

    # Éxito: devolvemos lo que envía Kraken.
    return jsonify({
        "error": kraken_json["error"],   # debería ser una lista vacía si fue exitoso
        "result": kraken_json["result"]
    }), 200


if __name__ == '__main__':
    # Ejecuta la app Flask en modo debug, en el puerto 5000
    app.run(debug=True, port=5000)
