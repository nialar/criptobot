import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = "7974145724:AAEh2D3VaYY8KYgZoBjBoESs762Eh2ev-3E"
DEEPSEEK_API_KEY = "sk-a7a6f28fbd2449f791556dd0b1db4212"
USER_ID = 7564194754

tokens = {
    "popcat": {"id": "popcat", "amount": 2249.51, "alerta_alta": 0.40, "alerta_baja": 0.30},
    "mew": {"id": "cat-in-a-dogs-world", "amount": 307850.59, "alerta_alta": 0.0032, "alerta_baja": 0.0025},
    "mavia": {"id": "heroes-of-mavia", "amount": 315.72, "alerta_alta": 0.17, "alerta_baja": 0.12},
    "arb": {"id": "arbitrum", "amount": 2436.28, "alerta_alta": None, "alerta_baja": None},
    "near": {"id": "near", "amount": 78.99, "alerta_alta": None, "alerta_baja": None},
    "btc": {"id": "bitcoin", "amount": 0, "alerta_alta": None, "alerta_baja": None},
    "eth": {"id": "ethereum", "amount": 0, "alerta_alta": None, "alerta_baja": None}
}

def get_prices():
    ids = ",".join([t["id"] for t in tokens.values()])
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur"
    return requests.get(url).json()
    
    
    
def portfolio(update, context):
    prices = get_prices()
    print(prices)
    msg = "📊 Tu portfolio actual:\n"
    total = 0
    for symbol, data in tokens.items():
        amount = data["amount"]
        price = prices.get(data["id"], {}).get("eur", None)
        if price is None:
            msg += f"- {symbol.upper()}: Precio no disponible\n"
            continue
        value = amount * price
        total += value
        msg += f"- {symbol.upper()}: {amount:.2f} → {value:.2f}€ (Precio: {price:.4f})\n"
    msg += f"💼 Total: {total:.2f}€"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3:
        await update.message.reply_text("Usa: /comprar token cantidad precio")
        return
    token, cantidad, precio = context.args
    cantidad = float(cantidad)
    if token not in tokens:
        await update.message.reply_text("Token no reconocido.")
        return
    tokens[token]["amount"] += cantidad
    await update.message.reply_text(f"✅ Añadido: {cantidad} {token.upper()} a {precio}€")

async def analizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pregunta = " ".join(context.args)
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": pregunta}],
        "temperature": 0.7
    }
    res = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data)
    reply = res.json()["choices"][0]["message"]["content"]
    await update.message.reply_text(reply)

async def enviar_alertas(context: ContextTypes.DEFAULT_TYPE):
    prices = get_prices()
    mensajes = []
    for symbol, data in tokens.items():
        price = prices[data["id"]]["eur"]
        if data["alerta_alta"] and price >= data["alerta_alta"]:
            mensajes.append(f"🚀 {symbol.upper()} ha superado {data['alerta_alta']}€ → Ahora: {price:.4f}€")
        if data["alerta_baja"] and price <= data["alerta_baja"]:
            mensajes.append(f"⚠️ {symbol.upper()} ha caído por debajo de {data['alerta_baja']}€ → Ahora: {price:.4f}€")
    if mensajes:
        msg = "\n".join(mensajes)
        await context.bot.send_message(chat_id=USER_ID, text=msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(CommandHandler("comprar", comprar))
    app.add_handler(CommandHandler("analiza", analizar))

    # Programar alertas
    job_queue = app.job_queue
    job_queue.run_repeating(enviar_alertas, interval=900, first=10)

    # Ejecutar bot hasta Ctrl+C
    app.run_polling()
