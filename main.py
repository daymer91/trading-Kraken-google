import os
from flask import Flask, request, jsonify
import logging
import requests  # Para integrar con la API de Kraken o cualquier otro servicio

app = Flask(__name__)

# Configuración
WEBHOOK_SECRET = os.getenv('TRADINGVIEW_WEBHOOK_SECRET', '3262dadcf9880410a9e11d6d61cffe29a19a2467820a0ef70f799b1ddbb9fa44')
KRAKEN_API_URL = "https://api.kraken.com/0/private/Order"  # URL base de Kraken

# Configurar el registro
logging.basicConfig(level=logging.INFO)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Leer datos de la solicitud
        data = request.get_json()

        if not data or 'secret' not in data:
            logging.warning("Solicitud sin datos válidos.")
            return jsonify({"error": "Invalid request"}), 400

        # Validar secreto
        if data.get('secret') != WEBHOOK_SECRET:
            logging.warning("Secreto inválido: %s", data.get('secret'))
            return jsonify({"error": "Invalid secret"}), 403

        # Procesar datos de alerta
        action = data.get('action')
        symbol = data.get('symbol', 'unknown')
        logging.info("Alerta recibida: Acción=%s, Símbolo=%s", action, symbol)

        # Lógica de integración con Kraken (ejemplo)
        if action in ['buy', 'sell']:
            response = send_order_to_kraken(action, symbol)
            return jsonify({"message": "Order sent to Kraken", "details": response}), 200

        return jsonify({"message": "Webhook received"}), 200

    except Exception as e:
        logging.error("Error procesando la solicitud: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500


def send_order_to_kraken(action, symbol):
    """Simulación de una función que envía una orden a Kraken."""
    payload = {
        "pair": symbol,
        "type": action,
        "ordertype": "market",
        "volume": "0.01"  # Ejemplo de volumen
    }
    headers = {
        "API-Key": os.getenv('KRAKEN_API_KEY', ''),
        "API-Sign": os.getenv('KRAKEN_API_SECRET', '')
    }
    try:
        # Enviar solicitud simulada
        response = requests.post(KRAKEN_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("Error enviando orden a Kraken: %s", str(e))
        return {"error": str(e)}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
