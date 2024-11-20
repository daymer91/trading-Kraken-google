import krakenex
import talib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Configuración de la API de Kraken
kraken_api = krakenex.API()
kraken_api.api_key = os.getenv('KRAKEN_API_KEY')
kraken_api.api_secret = os.getenv('KRAKEN_SECRET_KEY')

# Pares y capital predeterminado
TRADING_PAIR = 'XXBTZUSD'
CAPITAL = 100
RISK_PERCENT = 0.015  # 1.5% de riesgo

def get_data(pair, interval=15):
    """Función para obtener datos históricos de Kraken."""
    ohlc = kraken_api.query_public('OHLC', {'pair': pair, 'interval': interval})
    if ohlc['error']:
        return None
    return pd.DataFrame(ohlc['result'][pair], columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])

def calculate_indicators(df):
    """Calcula los indicadores técnicos."""
    df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)
    df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    df['SMA_Fast'] = talib.SMA(df['close'], timeperiod=9)
    df['SMA_Slow'] = talib.SMA(df['close'], timeperiod=21)
    return df

def execute_order(order_type, volume):
    """Función para ejecutar una orden en Kraken."""
    response = kraken_api.query_private('AddOrder', {
        'pair': TRADING_PAIR,
        'type': order_type,
        'ordertype': 'market',
        'volume': volume
    })
    if response.get('error'):
        return {'success': False, 'error': response['error']}
    return {'success': True, 'data': response['result']}

def check_trade_conditions(df):
    """Verifica las condiciones de trading."""
    last_row = df.iloc[-1]
    long_condition = (
        last_row['RSI'] < 65 and
        last_row['ADX'] > 20 and
        last_row['SMA_Fast'] > last_row['SMA_Slow']
    )
    short_condition = (
        last_row['RSI'] > 35 and
        last_row['ADX'] > 20 and
        last_row['SMA_Fast'] < last_row['SMA_Slow']
    )
    return long_condition, short_condition

@app.route('/execute_trade', methods=['POST'])
def execute_trade():
    data = request.get_json()
    volume = data.get("volume", 0.001)

    # Obtener y procesar los datos de mercado
    df = get_data(TRADING_PAIR)
    if df is None:
        return jsonify({"error": "No se pudieron obtener datos de Kraken"}), 500

    df = calculate_indicators(df)

    # Verificar condiciones de trading
    long_condition, short_condition = check_trade_conditions(df)

    # Ejecutar la orden según las condiciones
    if long_condition:
        result = execute_order("buy", volume)
        action = "compra"
    elif short_condition:
        result = execute_order("sell", volume)
        action = "venta"
    else:
        return jsonify({"message": "No hay condiciones para operar"}), 400

    # Respuesta en función del resultado de la orden
    if result['success']:
        return jsonify({"success": True, "message": f"Orden de {action} ejecutada", "data": result['data']}), 200
    else:
        return jsonify({"success": False, "error": result['error']}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
