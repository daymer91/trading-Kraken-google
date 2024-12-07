const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios'); // Para integrar con Kraken u otros servicios
require('dotenv').config(); // Cargar variables de entorno desde un archivo .env

const app = express();
const PORT = process.env.PORT || 5000;

// Configuración
const WEBHOOK_SECRET = process.env.TRADINGVIEW_WEBHOOK_SECRET || "3262dadcf9880410a9e11d6d61cffe29a19a2467820a0ef70f799b1ddbb9fa44";
const KRAKEN_API_URL = "https://api.kraken.com/0/private/Order";

// Middleware
app.use(bodyParser.json());

// Ruta principal para recibir webhooks
app.post('/webhook', async (req, res) => {
    try {
        const { secret, action, symbol } = req.body;

        // Validar secreto
        if (secret !== WEBHOOK_SECRET) {
            console.warn("Secreto inválido recibido:", secret);
            return res.status(403).json({ error: "Invalid secret" });
        }

        console.log(`Alerta recibida: Acción=${action}, Símbolo=${symbol}`);

        // Procesar acción
        if (action === 'buy' || action === 'sell') {
            const response = await sendOrderToKraken(action, symbol);
            return res.status(200).json({ message: "Order sent to Kraken", details: response });
        }

        res.status(200).json({ message: "Webhook received" });
    } catch (error) {
        console.error("Error procesando el webhook:", error);
        res.status(500).json({ error: "Internal server error" });
    }
});

// Función para enviar órdenes a Kraken
async function sendOrderToKraken(action, symbol) {
    const payload = {
        pair: symbol,
        type: action,
        ordertype: "market",
        volume: "0.01", // Ejemplo de volumen
    };
    const headers = {
        "API-Key": process.env.KRAKEN_API_KEY,
        "API-Sign": process.env.KRAKEN_API_SECRET,
    };
    try {
        const response = await axios.post(KRAKEN_API_URL, payload, { headers });
        return response.data;
    } catch (error) {
        console.error("Error enviando orden a Kraken:", error);
        return { error: error.message };
    }
}

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`Servidor escuchando en el puerto ${PORT}`);
});
