from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received data:", data)
    return jsonify({"status": "success", "received": data}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80)
