import flask
from flask import request, jsonify
import hashlib
import hmac
import base64
import time
import requests
import logging
from dotenv import load_dotenv
import os
import asyncio

# Cargar variables de entorno
load_dotenv()

app = flask.Flask("main")

# Configuración inicial
API_KEY = os.getenv("API_KEY", "YOUR_API_KEY")
API_SECRET = os.getenv("API_SECRET", "YOUR_API_SECRET")
BASE_URL = "https://api.kraken.com"
DEFAULT_PAIR = os.getenv("DEFAULT_PAIR", "XBTUSD")  # Par predeterminado
DEFAULT_VOLUME = float(os.getenv("DEFAULT_VOLUME", 2))  # Tamaño fijo de la operación

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='kraken_server.log', filemode='a')
logger = logging.getLogger()

# Métricas globales
metrics = {
    "orders_sent": 0,
    "simulations": 0,
    "errors": 0
}

# Funciones auxiliares
def generate_signature(api_path, data, secret):
    post_data = data.encode('utf-8')
    message = api_path.encode('utf-8') + hashlib.sha256(post_data).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    return base64.b64encode(mac.digest()).decode()

async def send_order(order_type, volume, pair, price=None):
    api_path = "/0/private/AddOrder"
    url = BASE_URL + api_path
    nonce = str(int(time.time() * 1000))

    data = {
        "nonce": nonce,
        "ordertype": order_type,
        "type": "buy" if order_type == "market" else "sell",
        "volume": volume,
        "pair": pair
    }
    if price:
        data["price"] = price

    headers = {
        "API-Key": API_KEY,
        "API-Sign": generate_signature(api_path, "nonce=" + nonce + "&" + "&".join([f"{k}={v}" for k, v in data.items()]), API_SECRET)
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        metrics["orders_sent"] += 1
        logger.info(f"Order sent successfully: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        metrics["errors"] += 1
        logger.error(f"Error sending order: {e}")
        return {"error": str(e)}

# Rutas del servidor
@app.route('/')
def home():
    return "¡Bienvenido al servidor de trading de Kraken!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        metrics["errors"] += 1
        logger.warning("No data received in webhook")
        return jsonify({"error": "No data received"}), 400

    try:
        order_type = data.get("type")
        entry = data.get("entry")
        stop_loss = data.get("sl")
        take_profit = data.get("tp")
        volume = data.get("volume", DEFAULT_VOLUME)
        pair = data.get("pair", DEFAULT_PAIR)

        logger.info(f"Received webhook: {data}")

        # Simulación para pruebas locales
        response = {
            "order_type": order_type,
            "entry_price": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "volume": volume,
            "pair": pair,
            "status": "Webhook received successfully"
        }

        return jsonify(response), 200

    except Exception as e:
        metrics["errors"] += 1
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "Server is running"})

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()

    if not data:
        metrics["errors"] += 1
        logger.warning("No data received for simulation")
        return jsonify({"error": "No data received"}), 400

    try:
        order_type = data.get("type")
        entry = data.get("entry")
        stop_loss = data.get("sl")
        take_profit = data.get("tp")
        volume = data.get("volume", DEFAULT_VOLUME)
        pair = data.get("pair", DEFAULT_PAIR)

        simulated_result = {
            "order_type": order_type,
            "entry_price": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "volume": volume,
            "pair": pair,
            "status": "Simulated successfully"
        }

        metrics["simulations"] += 1
        logger.info(f"Simulation result: {simulated_result}")
        return jsonify(simulated_result)

    except Exception as e:
        metrics["errors"] += 1
        logger.error(f"Error during simulation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/metrics', methods=['GET'])
def get_metrics():
    return jsonify(metrics)

if __name__ == '__main__':
    with app.test_request_context():
        print(app.url_map)
    app.run(debug=True, host='0.0.0.0', port=5000)
