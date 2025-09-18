import requests
import time
import telebot

# Configurações do bot
TOKEN = "8064880951:AAG2t9sq6PwOeQpMnDWgTI-DuvGj5QBhdLU"
CHAT_ID = "-1002550073701"
bot = telebot.TeleBot(TOKEN)

# URL do Tipminer
URL = "https://www.tipminer.com/br/historico/blaze/double"

# Função para pegar os últimos resultados
def get_results():
    try:
        r = requests.get(URL, timeout=10)
        if r.status_code == 200:
            # Procura os números e cores no HTML
            # Tipminer mostra <div class="... red">n</div> ou <div class="... black">n</div>
            html = r.text
            results = []
            lines = html.split("\n")
            for line in lines:
                if "result" in line and ("red" in line or "black" in line or "white" in line):
                    if "red" in line:
                        results.append("vermelho")
                    elif "black" in line:
                        results.append("preto")
                    elif "white" in line:
                        results.append("branco")
                if len(results) >= 20:  # só pega os 20 últimos
                    break
            return results
    except Exception as e:
        print("Erro ao buscar resultados:", e)
    return []

def send(msg):
    bot.send_message(CHAT_ID, msg, parse_mode="HTML")

# Lógica principal
def main():
    last_signal_time = 0
    gale_count = 0
    aposta = None

    while True:
        resultados = get_results()
        if len(resultados) < 3:
            time.sleep(5)
            continue

        ultimos = resultados[:3]  # pega os 3 últimos
        print("Últimos:", ultimos)

        # Se ainda não tem aposta, verifica padrão
        if aposta is None:
            if ultimos[0] == ultimos[1] and ultimos[0] in ["vermelho", "preto"]:
                # Sinal encontrado
                aposta = "preto" if ultimos[0] == "vermelho" else "vermelho"
                gale_count = 0
                send(f"🎯 <b>Entrada encontrada!</b>\nEntre na cor: {aposta.upper()}\nGales: até 2")
                last_signal_time = time.time()

        else:
            # Já temos aposta, verificar resultado do último giro
            ultimo_resultado = ultimos[0]
            if ultimo_resultado == aposta:
                send("✅ GREEN na cor " + aposta.upper())
                aposta = None
            else:
                if gale_count < 2:
                    gale_count += 1
                    send(f"⚠️ Gale {gale_count} ativado! Continuar na cor: {aposta.upper()}")
                else:
                    send("❌ RED – não bateu em 2 gales.")
                    aposta = None

        time.sleep(10)

if __name__ == "__main__":
    send("🤖 Bot iniciado e monitorando padrões no Double!")
    main()
