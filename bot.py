import os
import time
import requests
from bs4 import BeautifulSoup
import telebot

# Configurações do bot
TOKEN = os.getenv("BOT_TOKEN", "8064880951:AAG2t9sq6PwOeQpMnDWgTI-DuvGj5QBhdLU")
CHAT_ID = os.getenv("CHAT_ID", "-1002550073701")
bot = telebot.TeleBot(TOKEN)

last_two = []
entrada_atual = None
gales = 0

TIPMINER_URL = "https://www.tipminer.com/br/historico/blaze/double"

def get_results_html():
    try:
        resp = requests.get(TIPMINER_URL, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        if resp.status_code != 200:
            print("Erro HTTP do Tipminer:", resp.status_code)
            return []
        soup = BeautifulSoup(resp.text, "html.parser")

        # Ajustar para pegar os últimos resultados: número + cor
        # Tipminer exibe resultados na tabela/historico com classes ou tags onde aparece "red", "black", etc.
        # Exemplo de seleção genérica:
        results = []
        # Encontrar elementos que contenham as cores. Pode mudar dependendo da estrutura do HTML do site.
        # Ex: <td class="color red"> ou <div class="result red">, etc.
        items = soup.find_all("span", {"class": ["color red", "color black", "color white"]})
        # Se não encontrar, pode ter que usar outra tag, como div ou td ou li, depende
        if not items:
            items = soup.find_all("td", class_=["red", "black", "white"])
        for it in items[:5]:  # pega os 5 mais recentes
            cls = it.get("class")
            cor = None
            if "red" in cls:
                cor = "vermelho"
            elif "black" in cls:
                cor = "preto"
            elif "white" in cls:
                cor = "branco"
            if cor:
                results.append(cor)
        return results
    except Exception as e:
        print("Erro ao fazer scraping:", e)
        return []

def send_msg(txt):
    try:
        bot.send_message(CHAT_ID, txt, parse_mode="HTML")
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def check_and_signal():
    global last_two, entrada_atual, gales

    results = get_results_html()
    if not results:
        print("Nenhum resultado captado")
        return

    print("Resultados captados:", results)

    # pegar os 2 primeiros (mais recentes)
    two = results[0:2]

    # se repetiu o mesmo par, não repetir
    if two == last_two:
        return
    last_two = two

    # lógica de sinal
    if entrada_atual is None:
        if two == ["vermelho", "vermelho"]:
            entrada_atual = "preto"
            gales = 0
            send_msg(f"🎯 Entrada detectada!\nCor: PRETO (porque 2 vermelhos seguidos)\n🔁 Até 2 gales")
        elif two == ["preto", "preto"]:
            entrada_atual = "vermelho"
            gales = 0
            send_msg(f"🎯 Entrada detectada!\nCor: VERMELHO (porque 2 pretos seguidos)\n🔁 Até 2 gales")
    else:
        # já temos entrada, verificar resultado seguinte
        # esperar que o novo resultado venha
        novo = results[0]
        if novo == entrada_atual:
            send_msg(f"✅ GREEN! Acertamos no {entrada_atual.upper()}")
            entrada_atual = None
            gales = 0
        else:
            if gales < 2:
                gales += 1
                send_msg(f"⚠️ Gale {gales} ativado! Ainda na cor {entrada_atual.upper()}")
            else:
                send_msg(f"❌ RED! Não bateu em 2 gales. Entrada {entrada_atual.upper()}")
                entrada_atual = None
                gales = 0

def main():
    send_msg("🤖 Bot iniciado e monitorando padrões no Blaze Double!")
    print("Bot iniciado e monitorando padrões no Blaze Double!")
    while True:
        try:
            check_and_signal()
        except Exception as e:
            print("Erro no loop principal:", e)
        time.sleep(12)  # espera 12 segundos antes de checar de novo

if __name__ == "__main__":
    main()
