import os
import time
import hashlib
import hmac
import base64
import requests
import urllib.parse
from flask import Flask, request, jsonify
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Cargar variables de entorno
load_dotenv()

# Inicialización de Flask
app = Flask(__name__)

# Configuración de los logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Claves API y configuración del webhook
TRADINGVIEW_WEBHOOK_SECRET = os.getenv("TRADINGVIEW_WEBHOOK_SECRET", "3262dadcf9880410a9e11d6d61cffe29a19a2467820a0ef70f799b1ddbb9fa44")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", "tu_api_key_de_kraken")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET", "tu_api_secret_de_kraken")

@app.route('/', methods=['GET'])
def home():
    return "Servidor Flask activo.", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Validar que los datos son JSON
        data = request.get_json()
        if data is None:
            app.logger.warning("Solicitud sin JSON recibida.")
            return jsonify({"error": "No JSON received"}), 400

        # Validar el secreto
        secret = data.get("secret")
        if secret != TRADINGVIEW_WEBHOOK_SECRET:
            app.logger.warning(f"Secreto inválido: {secret}")
            return jsonify({"error": "Invalid secret"}), 403

        # Leer acción y símbolo del payload
        action = data.get("action")
        symbol = data.get("symbol")

        if not action or not symbol:
            app.logger.warning("Datos incompletos en el payload del webhook.")
            return jsonify({"error": "Incomplete data"}), 400

        app.logger.info(f"Webhook recibido: acción={action}, símbolo={symbol}")

        # Procesar la orden si la acción es válida
        if action == "buy" and symbol == "BTCUSD":
            app.logger.info("Realizando una orden de compra de BTC/USD.")
            response = realizar_orden_kraken("buy", "XBTUSD", 0.01)
            if "error" in response and response["error"]:
                app.logger.error(f"Error de Kraken: {response['error']}")
                return jsonify({"error": response["error"]}), 500
            return jsonify({"status": "order placed", "response": response}), 200

        if action == "sell" and symbol == "BTCUSD":
            app.logger.info("Realizando una orden de venta de BTC/USD.")
            response = realizar_orden_kraken("sell", "XBTUSD", 0.01)
            if "error" in response and response["error"]:
                app.logger.error(f"Error de Kraken: {response['error']}")
                return jsonify({"error": response["error"]}), 500
            return jsonify({"status": "order placed", "response": response}), 200

        app.logger.info("Solicitud procesada correctamente.")
        return jsonify({"status": "received"}), 200

    except Exception as e:
        app.logger.error(f"Error procesando la solicitud: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def realizar_orden_kraken(action, pair, volume):
    url = "https://api.kraken.com/0/private/AddOrder"

    # Generar parámetros para la orden
    params = {
        'nonce': str(int(time.time() * 1000)),
        'pair': pair,
        'type': action,
        'ordertype': 'market',
        'volume': str(volume)
    }

    # Crear la firma
    post_data = urllib.parse.urlencode(params).encode()
    path = "/0/private/AddOrder"
    message = (str(params['nonce']) + post_data.decode()).encode()
    secret = base64.b64decode(KRAKEN_API_SECRET)
    signature = hmac.new(secret, hashlib.sha512, path.encode() + message, hashlib.sha512).digest()

    headers = {
        'API-Key': KRAKEN_API_KEY,
        'API-Sign': base64.b64encode(signature).decode()
    }

    try:
        # Hacer la solicitud a Kraken
        response = requests.post(url, data=params, headers=headers, timeout=10)
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("error"):
            app.logger.error(f"Errores de Kraken: {response_data['error']}")
        return response_data
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error en la solicitud a Kraken: {str(e)}")
        return {"error": str(e)}

def obtener_precio_actual(pair):
    url = "https://api.kraken.com/0/public/Ticker"
    params = {'pair': pair}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        precio_actual = data['result'][pair]['c'][0]  # Precio actual
        return float(precio_actual)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error obteniendo precio de Kraken: {str(e)}")
        return None

def monitorear_mercado():
    precio_actual = obtener_precio_actual("XBTUSD")
    if precio_actual:
        app.logger.info(f"Precio actual de XBT/USD: {precio_actual}")
        # Aquí puedes agregar lógica para ejecutar órdenes basadas en estrategias.

scheduler = BackgroundScheduler()
scheduler.add_job(monitorear_mercado, 'interval', minutes=1)
scheduler.start()

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
