import os

# Obtener la variable de entorno
webhook_secret = os.getenv("TRADINGVIEW_WEBHOOK_SECRET")

# Verificar si está configurada y mostrar su valor
if webhook_secret:
    print(f"El secreto de TradingView es: {webhook_secret}")
else:
    print("La variable de entorno TRADINGVIEW_WEBHOOK_SECRET no está configurada.")
