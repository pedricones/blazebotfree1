import requests
import time
import telebot
from bs4 import BeautifulSoup

# === CONFIG ===
TOKEN = "8064880951:AAG2t9sq6PwOeQpMnDWgTI-DuvGj5QBhdLU"
CHAT_ID = -1002550073701
URL = "https://www.tipminer.com/br/historico/blaze/double"

MAX_GALES = 2

bot = telebot.TeleBot(TOKEN)
ultimo_sinal = None
gale_atual = 0

def get_results():
    """Pega últimos resultados do tipminer"""
    r = requests.get(URL, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    balls = soup.select(".ball")
    results = []
    for b in balls[:20]:
        if "red" in b["class"]:
            results.append("vermelho")
        elif "black" in b["class"]:
            results.append("preto")
        elif "white" in b["class"]:
            results.append("branco")
    return results

def analisar_padrao(seq):
    """Verifica 2 cores seguidas"""
    if len(seq) < 2: return None
    if seq[0] == seq[1] and seq[0] in ["vermelho","preto"]:
        return "preto" if seq[0] == "vermelho" else "vermelho"
    return None

def main():
    global ultimo_sinal, gale_atual
    while True:
        try:
            seq = get_results()
            if not seq: 
                time.sleep(8)
                continue

            entrada = analisar_padrao(seq)

            # Novo sinal detectado
            if entrada and entrada != ultimo_sinal:
                bot.send_message(
                    CHAT_ID,
                    f"🎯 SINAL DETECTADO\n👉 Entrar no {entrada.upper()}\nProteção: Branco"
                )
                ultimo_sinal = entrada
                gale_atual = 0

            # Se já temos sinal em aberto, verificar resultado
            if ultimo_sinal:
                if seq[0] == ultimo_sinal:
                    bot.send_message(CHAT_ID, "✅ GREEN")
                    ultimo_sinal = None
                else:
                    if gale_atual < MAX_GALES:
                        gale_atual += 1
                        bot.send_message(CHAT_ID, f"🔄 Gale {gale_atual} no {ultimo_sinal.upper()}")
                    else:
                        bot.send_message(CHAT_ID, "❌ RED")
                        ultimo_sinal = None
                        gale_atual = 0

        except Exception as e:
            print("Erro:", e)

        time.sleep(8)

if __name__ == "__main__":
    main()
