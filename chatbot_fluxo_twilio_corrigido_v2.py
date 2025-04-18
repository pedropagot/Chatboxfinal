
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Chatbot SEFAZ-MA está ativo!"

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip().lower()
    from_number = request.values.get("From")
    resp = MessagingResponse()
    msg = resp.message()

    session = sessions.get(from_number, {"step": 0})
    step = session["step"]

    if step == 0:
        if any(greet in incoming_msg for greet in GREETINGS):
            session["step"] = 1
            msg.body("👋 Olá! Bem-vindo ao atendimento automatizado do setor de Trânsito.\n\n📌 Este canal é exclusivo para tratar de Mercadorias em Trânsito retidas em Postos Fiscais do Estado do Maranhão.\n\nAlguma mercadoria ou veículo foi retido em Posto Fiscal do Estado do Maranhão?\n[1] Sim\n[2] Não")
        else:
            msg.body("Olá! Para iniciar o atendimento, por favor envie uma saudação como 'oi', 'olá', 'bom dia'...")
            session["step"] = 0

    elif step == 1:
        if incoming_msg == "1":
            session["step"] = 2
            msg.body("Em qual Posto Fiscal está retida a mercadoria ou o veículo?\n[1] Estiva\n[2] Timon\n[3] Itinga\n[4] Quatro Bocas\n[5] Barão de Grajaú\n[6] Piranji\n[7] Estreito")
        elif incoming_msg == "2":
            msg.body("❗Infelizmente não podemos atender a sua solicitação.\nEste canal é exclusivo para tratar de mercadorias em trânsito retidas em postos fiscais do Estado.\n\nMais informações: https://sistemas1.sefaz.ma.gov.br/portalsefaz/jsp/pagina/pagina.jsf?codigo=1585")
            session["step"] = -1
        else:
            msg.body("Por favor, selecione uma opção válida: [1] Sim ou [2] Não")

    elif step == 2:
        if incoming_msg in [str(i) for i in range(1, 8)]:
            session["posto"] = incoming_msg
            session["step"] = 3
            msg.body("Possui inscrição estadual?\n[1] Sim\n[2] Não")
        else:
            msg.body("Por favor, selecione uma opção válida: [1] a [7]")

    elif step == 3:
        if incoming_msg == "1":
            session["step"] = 4
            msg.body("Digite a sua inscrição estadual (apenas números):")
        elif incoming_msg == "2":
            session["step"] = 5
            msg.body("Digite o CNPJ/CPF (apenas números):")
        else:
            msg.body("Por favor, selecione uma opção válida: [1] Sim ou [2] Não")

    elif step == 4:
        if re.fullmatch(r"[\d\s.-]+", incoming_msg):
            session["ie"] = incoming_msg
            session["step"] = 6
            msg.body("📝Por favor, relate brevemente a situação e, se necessário, envie os documentos relacionados (NFe, CTe, MDFe, etc.).")
        else:
            msg.body("Por favor, digite apenas os números da inscrição estadual.")

    elif step == 5:
        if re.fullmatch(r"[\d\s.-]+", incoming_msg):
            session["cpf_cnpj"] = incoming_msg
            session["step"] = 6
            msg.body("📝Por favor, relate brevemente a situação e, se necessário, envie os documentos relacionados (NFe, CTe, MDFe, etc.).")
        else:
            msg.body("Por favor, digite apenas os números do CPF/CNPJ.")

    elif step == 6:
        session["relato"] = incoming_msg
        session["step"] = 7
        posto = session.get("posto", "[não informado]")
        identificador = session.get("ie") or session.get("cpf_cnpj") or "[não informado]"
        msg.body(f"📨 Obrigado pelas informações!\n\nResumo do atendimento:\n- Posto Fiscal: {posto}\n- IE/CPF/CNPJ: {identificador}\n- Relato: {incoming_msg}\n\n🛠️ Seu atendimento foi encaminhado para análise da equipe interna.\n⏳ Em breve, um atendente entrará em contato.")

    sessions[from_number] = session
    return str(resp)

sessions = {}
GREETINGS = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
