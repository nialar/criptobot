import requests
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ======== CONFIGURACIÓN ==========
TELEGRAM_TOKEN = "7974145724:AAEh2D3VaYY8KYgZoBjBoESs762Eh2ev-3E"
USER_ID = 7564194754
DEEPSEEK_API_KEY = "sk-a7a6f28fbd2449f791556dd0b1db4212"

tokens = {
    "popcat": {"id": "popcat", "amount": 2249.51},
    "mew": {"id": "cat-in-a-dogs-world", "amount": 307850.59},
    "mavia": {"id": "heroes-of-mavia", "amount": 315.72},
    "arb": {"id": "arbitrum", "amount": 2436.28},
    "near": {"id": "near", "amount": 78.99},
    "btc": {"id": "bitcoin", "amount": 0},
    "eth": {"id": "ethereum", "amount": 0}
}

DEEPSEEK_PROMPT = (
    DEEPSEEK_PROMPT = (
    "Eres mi IA personal experta en criptomonedas y blockchain. "
    "Habla siempre de manera directa, actual y con datos relevantes para jóvenes traders. "
    "Si puedes meter humor de vez en cuando, hazlo. Responde SOLO sobre temas de cripto y intenta no hablar de otros temas.
    "Unai jefe tu eres su asistente de acuerdo? haz todo lo que el te pida"
)

)

def get_prices():
    ids = ",".join([t["id"] for t in tokens.values()])
    url_cg = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur"
    try:
        res = requests.get(url_cg, timeout=3)
        data = res.json()
        if any(k in data and "eur" in data[k] for k in [t["id"] for t in tokens.values()]):
            return {k: {"eur": data.get(k, {}).get("eur")} for k in [t["id"] for t in tokens.values()]}
    except Exception:
        pass

    id_map_paprika = {
        "popcat": "popcat-popcat",
        "cat-in-a-dogs-world": "cat-in-a-dogs-world-mew",
        "heroes-of-mavia": "heroes-of-mavia-mavia",
        "arbitrum": "arbitrum-arbitrum",
        "near": "near-near",
        "bitcoin": "btc-bitcoin",
        "ethereum": "eth-ethereum"
    }
    prices = {}
    for symbol, id_paprika in id_map_paprika.items():
        try:
            url_cp = f"https://api.coinpaprika.com/v1/tickers/{id_paprika}"
            res = requests.get(url_cp, timeout=3)
            data = res.json()
            if "quotes" in data and "EUR" in data["quotes"]:
                prices[symbol] = {"eur": data["quotes"]["EUR"]["price"]}
        except Exception:
            continue
    if prices:
        return prices

    return {}

async def portfolio(update, context: ContextTypes.DEFAULT_TYPE):
    prices = get_prices()
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
    await update.message.reply_text(msg)

async def comprar(update, context: ContextTypes.DEFAULT_TYPE):
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

async def deepseek_reply(update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    prompt = [
        {"role": "system", "content": DEEPSEEK_PROMPT},
        {"role": "user", "content": user_message}
    ]
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    data = {
        "model": "deepseek-chat",
        "messages": prompt,
        "temperature": 0.3
    }
    res = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data)
    reply = res.json()["choices"][0]["message"]["content"]
    await update.message.reply_text(reply)

async def start():
    print("Bot iniciado 🚀")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(CommandHandler("comprar", comprar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, deepseek_reply))
    app.run_polling()

if __name__ == "__main__":
    main()
