import time
import hashlib
import hmac
import base64
import requests
import urllib.parse
from flask import Flask, request, jsonify
import logging

# Inicialización de Flask
app = Flask(__name__)

# Configuración de los logs
logging.basicConfig(level=logging.INFO)

# Clave secreta para la validación del webhook
TRADINGVIEW_WEBHOOK_SECRET = "3262dadcf9880410a9e11d6d61cffe29a19a2467820a0ef70f799b1ddbb9fa44"

# Claves API de Kraken (reemplázalas con tus claves reales)
api_key = '5BR049jMzfuhNvE22c9MRLOyVa+NlJr3UpXqe5S5Zfa/iHoQU0yy6oHk'
api_secret = 'JayudfYtCGqGlWDVM4uCkJgqSZc0RW0HWmyKfGcjNY//hxF3dAkeFNAzinrwsR8BeWqlv20emCurR8FRQ3Ewxw=='

@app.route('/', methods=['GET'])
def home():
    """Ruta para verificar que el servidor está activo"""
    return "Servidor Flask está activo y funcionando correctamente.", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Maneja las solicitudes POST del webhook"""
    try:
        data = request.get_json()
        if data is None:
            app.logger.warning("Solicitud sin JSON recibida.")
            return jsonify({"error": "No JSON received"}), 400

        secret = data.get("secret")
        if secret != TRADINGVIEW_WEBHOOK_SECRET:
            app.logger.warning("Secret inválido.")
            return jsonify({"error": "Invalid secret"}), 403

        action = data.get("action")
        symbol = data.get("symbol")

        app.logger.info(f"Webhook recibido: acción={action}, símbolo={symbol}")

        if action == "buy" and symbol == "BTCUSD":
            app.logger.info("Realizando una orden de compra de BTC/USD.")
            
            # Realizar la compra en Kraken
            response = realizar_orden_kraken(api_key, api_secret, "buy", "XBTUSD", 1.0)
            if "error" in response and response["error"]:
                app.logger.error(f"Error en la respuesta de Kraken: {response['error']}")
                return jsonify({"error": response["error"]}), 500
            
            return jsonify({"status": "order placed", "response": response}), 200

        return jsonify({"status": "received"}), 200

    except Exception as e:
        app.logger.error(f"Error procesando la solicitud: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def realizar_orden_kraken(api_key, api_secret, action, pair, volume):
    """Realiza una orden en Kraken"""
    url = 'https://api.kraken.com/0/private/AddOrder'

    params = {
        'nonce': str(int(time.time() * 1000)),
        'pair': pair,
        'type': action,
        'ordertype': 'market',
        'volume': str(volume)
    }

    # Crear el mensaje para la firma
    post_data = urllib.parse.urlencode(params)
    message = f"/0/private/AddOrder{post_data}".encode('utf-8')
    secret = base64.b64decode(api_secret)

    signature = hmac.new(
        secret,
        hashlib.sha256(str(params["nonce"]).encode("utf-8")).digest() + message,
        hashlib.sha512
    ).digest()

    headers = {
        'API-Key': api_key,
        'API-Sign': base64.b64encode(signature).decode()
    }

    # Realizar la solicitud a Kraken
    try:
        response = requests.post(url, data=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error en la solicitud a Kraken: {str(e)}")
        return {"error": str(e)}

# Configuración de producción con Waitress
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
