import os
import time
import requests
from bs4 import BeautifulSoup
import telebot

# Variáveis de ambiente (você pode deixar fixo também)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8064880951:AAG2t9sq6PwOeQpMnDWgTI-DuvGj5QBhdLU")
CHAT_ID = os.getenv("CHAT_ID", "-1002550073701")

bot = telebot.TeleBot(BOT_TOKEN)

# URL do Tipminer (Double Blaze)
URL = "https://www.tipminer.com/br/historico/blaze/double"

# Armazena últimos resultados para evitar duplicar sinais
last_check = []

def get_results():
    """Faz scraping dos últimos resultados do Tipminer"""
    try:
        response = requests.get(URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Pega os números + cores (ex: div com classe "dice red"/"dice black"/"dice white")
        results = soup.find_all("div", class_="dice")
        parsed = []

        for r in results[:10]:  # só pega os últimos 10
            number = r.text.strip()
            color = "vermelho"
            if "black" in r["class"]:
                color = "preto"
            elif "white" in r["class"]:
                color = "branco"
            parsed.append((number, color))

        return parsed
    except Exception as e:
        print("Erro ao pegar resultados:", e)
        return []

def check_pattern():
    """Verifica padrão: 2 vermelhos => aposta preto, 2 pretos => aposta vermelho"""
    global last_check
    results = get_results()

    if not results or len(results) < 2:
        return

    # Mostra no log do Render o que pegou
    print("Últimos captados:", results[:5])

    # Pega os 2 últimos
    last_two = [c for _, c in results[:2]]

    # Evita duplicar
    if last_two == last_check:
        return

    last_check = last_two

    # Aplica lógica
    if last_two == ["vermelho", "vermelho"]:
        send_signal("preto")
    elif last_two == ["preto", "preto"]:
        send_signal("vermelho")

def send_signal(cor):
    """Envia o sinal com até 2 gales"""
    try:
        msg = f"👉 Entrada detectada!\n🎯 Apostar no: {cor.upper()}\n📌 Estratégia: até 2 Gales"
        bot.send_message(CHAT_ID, msg)
        print("Sinal enviado:", msg)
    except Exception as e:
        print("Erro ao enviar sinal:", e)

def main():
    bot.send_message(CHAT_ID, "🤖 Bot iniciado e monitorando padrões no Blaze Double!")
    print("Bot rodando...")
    while True:
        check_pattern()
        time.sleep(15)  # verifica a cada 15s

if __name__ == "__main__":
    main()
