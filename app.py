import streamlit as st
import asyncio
import tempfile
import os
import re
from datetime import datetime
from groq import Groq
import edge_tts
import PyPDF2
import docx

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="AI Customer Service Suite | GlobalInternet.py",
    page_icon="🤖",
    layout="wide"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a192f 0%, #112240 100%);
        color: #ffffff;
    }
    .main-title {
        text-align: center;
        margin-bottom: 1rem;
    }
    .main-title h1 {
        color: #ffd966;
    }
    .main-title p {
        color: #a0b0c0;
    }
    .stButton>button {
        background-color: #e94560;
        color: white;
        border-radius: 30px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #ff6b6b;
    }
    .security-badge {
        background: #0a192f;
        border: 1px solid #00ebc7;
        border-radius: 30px;
        padding: 8px 15px;
        margin: 10px 0;
        text-align: center;
        color: #00ebc7;
        font-weight: bold;
    }
    .chat-message {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== LANGUAGE DICTIONARIES ==========
TEXTS = {
    "English": {
        "title": "🤖 AI Customer Service Suite",
        "subtitle": "Smart text, email, and voice support powered by your company guidelines",
        "intro_btn": "🎙️ Watch Introduction (AI Female Voice)",
        "intro_text": "Welcome to AI Customer Service Suite. This software helps companies automate customer support across text messages, emails, and phone/WhatsApp calls. You upload your company guidelines, and the AI answers every inquiry based on those policies. It works in English, French, and Spanish. You can connect your phone number via Twilio to answer WhatsApp chats and calls automatically. This tool saves time, improves response consistency, and works 24/7. This software was built by Gesner Deslandes, Engineer‑in‑Chief at GlobalInternet.py.",
        "sidebar_title": "Company Setup",
        "upload_guidelines": "Upload Guidelines (PDF, DOCX, TXT)",
        "guidelines_loaded": "✅ Guidelines loaded. AI will use them for all responses.",
        "no_guidelines": "⚠️ No guidelines uploaded yet. Please upload your company policies.",
        "api_key_warning": "⚠️ Missing Groq API key. Add GROQ_API_KEY to Streamlit secrets.",
        "twilio_info": "📞 Phone/WhatsApp Integration (Twilio Required)",
        "twilio_instruction": "To connect your phone number for voice and WhatsApp, configure Twilio webhook to point to: https://your-app.streamlit.app/webhook . This demo includes a test chat interface below.",
        "twilio_sid": "Twilio Account SID (optional for demo)",
        "twilio_auth": "Twilio Auth Token (optional for demo)",
        "twilio_phone": "Your Twilio Phone Number",
        "save_twilio": "Save Twilio Settings",
        "customer_chat": "💬 Customer Chat (Text / Email Simulation)",
        "customer_name": "Customer Name",
        "customer_email": "Customer Email (optional)",
        "customer_question": "Customer Question / Message",
        "send_text": "Send (Simulate Text/Email)",
        "ai_response": "🤖 AI Response",
        "footer": "© 2026 GlobalInternet.py – AI Customer Service Suite",
        "security_badge": "🔐 End‑to‑end encryption active",
        "lang": "Language",
        "guidelines_summary": "Guidelines Summary (first 500 chars):"
    },
    "French": {
        "title": "🤖 Suite de service client IA",
        "subtitle": "Support textuel, email et vocal intelligent basé sur vos politiques",
        "intro_btn": "🎙️ Regarder l'introduction (voix IA féminine)",
        "intro_text": "Bienvenue dans la Suite de service client IA. Ce logiciel aide les entreprises à automatiser le support client par SMS, emails et appels téléphoniques/WhatsApp. Vous téléchargez vos politiques, et l'IA répond à chaque demande selon ces règles. Fonctionne en anglais, français et espagnol. Vous pouvez connecter votre numéro via Twilio pour répondre aux appels et chats WhatsApp automatiquement. Cet outil fait gagner du temps, améliore la cohérence et travaille 24/7. Ce logiciel a été construit par Gesner Deslandes, ingénieur en chef chez GlobalInternet.py.",
        "sidebar_title": "Configuration entreprise",
        "upload_guidelines": "Télécharger les politiques (PDF, DOCX, TXT)",
        "guidelines_loaded": "✅ Politiques chargées. L'IA les utilisera pour toutes les réponses.",
        "no_guidelines": "⚠️ Aucune politique chargée. Veuillez télécharger vos directives.",
        "api_key_warning": "⚠️ Clé Groq API manquante. Ajoutez GROQ_API_KEY aux secrets Streamlit.",
        "twilio_info": "📞 Intégration téléphone/WhatsApp (Twilio requis)",
        "twilio_instruction": "Pour connecter votre numéro pour les appels vocaux et WhatsApp, configurez le webhook Twilio vers : https://votre-app.streamlit.app/webhook . Cette démo inclut une interface de chat de test ci‑dessous.",
        "twilio_sid": "Twilio Account SID (optionnel pour la démo)",
        "twilio_auth": "Twilio Auth Token (optionnel pour la démo)",
        "twilio_phone": "Votre numéro Twilio",
        "save_twilio": "Enregistrer les paramètres Twilio",
        "customer_chat": "💬 Chat client (simulation texte/email)",
        "customer_name": "Nom du client",
        "customer_email": "Email du client (optionnel)",
        "customer_question": "Question / message du client",
        "send_text": "Envoyer (simuler texte/email)",
        "ai_response": "🤖 Réponse IA",
        "footer": "© 2026 GlobalInternet.py – Suite service client IA",
        "security_badge": "🔐 Chiffrement de bout en bout actif",
        "lang": "Langue",
        "guidelines_summary": "Résumé des politiques (500 premiers caractères) :"
    },
    "Spanish": {
        "title": "🤖 Suite de servicio al cliente IA",
        "subtitle": "Soporte inteligente por texto, email y voz basado en sus políticas",
        "intro_btn": "🎙️ Ver introducción (voz IA femenina)",
        "intro_text": "Bienvenido a la Suite de servicio al cliente IA. Este software ayuda a las empresas a automatizar el soporte al cliente mediante mensajes de texto, correos electrónicos y llamadas telefónicas/WhatsApp. Usted sube sus políticas y la IA responde cada consulta según esas reglas. Funciona en inglés, francés y español. Puede conectar su número de teléfono a través de Twilio para responder chats y llamadas de WhatsApp automáticamente. Esta herramienta ahorra tiempo, mejora la consistencia y trabaja 24/7. Este software fue construido por Gesner Deslandes, ingeniero jefe de GlobalInternet.py.",
        "sidebar_title": "Configuración de la empresa",
        "upload_guidelines": "Subir políticas (PDF, DOCX, TXT)",
        "guidelines_loaded": "✅ Políticas cargadas. La IA las usará para todas las respuestas.",
        "no_guidelines": "⚠️ No se han cargado políticas. Suba sus directrices.",
        "api_key_warning": "⚠️ Falta la clave de Groq API. Agregue GROQ_API_KEY a los secretos de Streamlit.",
        "twilio_info": "📞 Integración telefónica/WhatsApp (requiere Twilio)",
        "twilio_instruction": "Para conectar su número para llamadas de voz y WhatsApp, configure el webhook de Twilio apuntando a: https://su-app.streamlit.app/webhook . Esta demo incluye una interfaz de chat de prueba a continuación.",
        "twilio_sid": "Twilio Account SID (opcional para la demo)",
        "twilio_auth": "Twilio Auth Token (opcional para la demo)",
        "twilio_phone": "Su número de Twilio",
        "save_twilio": "Guardar configuración de Twilio",
        "customer_chat": "💬 Chat con cliente (simulación texto/email)",
        "customer_name": "Nombre del cliente",
        "customer_email": "Correo electrónico del cliente (opcional)",
        "customer_question": "Pregunta / mensaje del cliente",
        "send_text": "Enviar (simular texto/email)",
        "ai_response": "🤖 Respuesta IA",
        "footer": "© 2026 GlobalInternet.py – Suite servicio al cliente IA",
        "security_badge": "🔐 Cifrado de extremo a extremo activo",
        "lang": "Idioma",
        "guidelines_summary": "Resumen de políticas (primeros 500 caracteres):"
    }
}

# ========== VOICE MAPPING (female) ==========
VOICE_MAP = {
    "English": "en-US-JennyNeural",
    "French": "fr-FR-DeniseNeural",
    "Spanish": "es-ES-ElviraNeural"
}

# ========== EXTRACT TEXT FROM UPLOADED FILE ==========
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    file_type = uploaded_file.type
    if file_type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    elif file_type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return ""

# ========== AI RESPONSE FUNCTION (Groq) ==========
def get_ai_response(question, guidelines, lang):
    if not guidelines:
        return "Please upload your company guidelines first. / Veuillez d'abord télécharger vos politiques. / Por favor, cargue primero sus políticas."
    
    system_prompt = f"""You are an AI customer service agent for a company. Answer the customer's question based ONLY on the following company guidelines. Be polite, helpful, and concise. If the question cannot be answered from the guidelines, say "I cannot find that information in our guidelines. Please contact a human agent." Respond in {lang}.

Guidelines:
{guidelines[:4000]}  # Limit to 4000 chars for token efficiency

Customer question: {question}

Answer:"""
    
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI error: {str(e)}"

# ========== TEXT TO SPEECH (female voice) ==========
async def text_to_speech(text, voice, output_path):
    comm = edge_tts.Communicate(text, voice)
    await comm.save(output_path)

def generate_audio(text, lang):
    voice = VOICE_MAP.get(lang, "en-US-JennyNeural")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp_path = tmp.name
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(text_to_speech(text, voice, tmp_path))
    loop.close()
    with open(tmp_path, "rb") as f:
        audio_bytes = f.read()
    os.unlink(tmp_path)
    return audio_bytes

# ========== INIT SESSION STATE ==========
if "guidelines_text" not in st.session_state:
    st.session_state.guidelines_text = ""
if "lang" not in st.session_state:
    st.session_state.lang = "English"
if "twilio_sid" not in st.session_state:
    st.session_state.twilio_sid = ""
if "twilio_auth" not in st.session_state:
    st.session_state.twilio_auth = ""
if "twilio_phone" not in st.session_state:
    st.session_state.twilio_phone = ""

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/null/customer-support.png", width=80)
    st.markdown("## **GlobalInternet.py**")
    st.markdown("**AI Customer Service Suite**")
    st.markdown("---")
    
    lang = st.selectbox("🌐 Language", ["English", "French", "Spanish"], key="lang_selector")
    if lang != st.session_state.lang:
        st.session_state.lang = lang
        st.rerun()
    texts = TEXTS[st.session_state.lang]
    
    st.markdown("---")
    st.markdown(f"### 🛡️ {texts['security_badge']}")
    st.markdown('<div class="security-badge">🔐 End‑to‑end encryption active</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader(texts["sidebar_title"])
    uploaded_file = st.file_uploader(texts["upload_guidelines"], type=["txt", "pdf", "docx"])
    if uploaded_file:
        guidelines = extract_text_from_file(uploaded_file)
        st.session_state.guidelines_text = guidelines
        st.success(texts["guidelines_loaded"])
        with st.expander(texts["guidelines_summary"]):
            st.write(guidelines[:500] + "...")
    else:
        st.warning(texts["no_guidelines"])
    
    st.markdown("---")
    st.markdown(f"### {texts['twilio_info']}")
    st.info(texts["twilio_instruction"])
    twilio_sid = st.text_input(texts["twilio_sid"], value=st.session_state.twilio_sid)
    twilio_auth = st.text_input(texts["twilio_auth"], type="password", value=st.session_state.twilio_auth)
    twilio_phone = st.text_input(texts["twilio_phone"], value=st.session_state.twilio_phone)
    if st.button(texts["save_twilio"], use_container_width=True):
        st.session_state.twilio_sid = twilio_sid
        st.session_state.twilio_auth = twilio_auth
        st.session_state.twilio_phone = twilio_phone
        st.success("Settings saved (for demo purposes). Real Twilio integration requires webhook.")
    
    st.markdown("---")
    st.markdown("Built by **Gesner Deslandes**, Engineer-in-Chief")
    st.markdown("📞 (509) 4738 5663")
    st.markdown("✉️ deslandes78@gmail.com")
    st.markdown("---")
    st.caption(texts["footer"])

# ========== MAIN PAGE ==========
st.markdown(f'<div class="main-title"><h1>{texts["title"]}</h1><p>{texts["subtitle"]}</p></div>', unsafe_allow_html=True)

# AI Voice Introduction
if st.button(texts["intro_btn"], use_container_width=True):
    with st.spinner("Generating voice introduction..."):
        audio = generate_audio(texts["intro_text"], st.session_state.lang)
        st.audio(audio, format="audio/mp3")
        st.success("Introduction played. You can listen again if needed.")

st.markdown("---")

# Check for Groq API key
if "GROQ_API_KEY" not in st.secrets:
    st.error(texts["api_key_warning"])
else:
    st.subheader(texts["customer_chat"])
    
    # Chat simulation
    with st.form("customer_form"):
        customer_name = st.text_input(texts["customer_name"], value="Jane Doe")
        customer_email = st.text_input(texts["customer_email"], value="jane@example.com")
        customer_question = st.text_area(texts["customer_question"], height=100)
        submitted = st.form_submit_button(texts["send_text"])
    
    if submitted and customer_question:
        if not st.session_state.guidelines_text:
            st.warning(texts["no_guidelines"])
        else:
            with st.spinner("AI is thinking..."):
                response = get_ai_response(customer_question, st.session_state.guidelines_text, st.session_state.lang)
            st.markdown(f"**{texts['ai_response']}**")
            st.markdown(f'<div class="chat-message">{response}</div>', unsafe_allow_html=True)
            
            # Optional: simulate email sending (for demo)
            if customer_email:
                st.info(f"📧 A copy of this response would be sent to {customer_email}")

# Note about voice call integration
st.markdown("---")
st.markdown("### 📞 Voice & WhatsApp Call Integration")
st.markdown("""
To connect a real phone number for voice calls or WhatsApp:
1. Sign up for a [Twilio](https://www.twilio.com) account.
2. Purchase a phone number with voice and WhatsApp capabilities.
3. Configure the Twilio webhook URL to point to your deployed app's `/webhook` endpoint (you will need to implement a simple Flask/FastAPI endpoint separately, or use a tool like ngrok for local testing).  
4. The AI response logic (using guidelines) will be triggered when a call or WhatsApp message arrives.

**For this demo**, the chat interface above simulates text/email responses. The same AI logic would apply to voice and WhatsApp if Twilio webhook is configured.
""")

st.markdown("---")
st.caption(f"*{texts['footer']}*")
