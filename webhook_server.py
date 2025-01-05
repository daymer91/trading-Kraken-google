from flask import Flask, request, jsonify
import time
import base64
import hashlib
import hmac
import requests
import json

app = Flask(__name__)

API_KEY = '5BR049jMzfuhNvE22c9MRLOyVa+NlJr3UpXqe5S5Zfa/iHoQU0yy6oHk'
API_SECRET = 'JayudfYtCGqGlWDVM4uCkJgqSZc0RW0HWmyKfGcjNY//hxF3dAkeFNAzinrwsR8BeWqlv20emCurR8FRQ3Ewxw=='
API_URL = 'https://api.kraken.com/0/private/AddOrder'

def generate_nonce():
    return str(int(time.time() * 1000))

def generate_signature(uri_path, data, secret):
    postdata = json.dumps(data, separators=(',', ':'))
    encoded = (data['nonce'] + postdata).encode()
    message = uri_path.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    return base64.b64encode(mac.digest()).decode()

@app.route('/webhook', methods=['POST'])
def webhook():
    alert_data = request.json
    pair = alert_data.get('pair', 'XXBTZUSD')
    ordertype = alert_data.get('ordertype', 'market')
    volume = alert_data.get('volume', '0.01')
    order_type = alert_data.get('type', 'buy')

    nonce = generate_nonce()
    data = {
        'nonce': nonce,
        'ordertype': ordertype,
        'type': order_type,
        'volume': volume,
        'pair': pair
    }

    headers = {
        'API-Key': API_KEY,
        'API-Sign': generate_signature('/0/private/AddOrder', data, API_SECRET)
    }

    response = requests.post(API_URL, headers=headers, data=data)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=5000)
