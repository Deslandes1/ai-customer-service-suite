import streamlit as st
import asyncio
import tempfile
import os
import re
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from groq import Groq
import edge_tts
import PyPDF2
import docx

# ============================================================================
# EMBEDDED COMPANY GUIDELINES (GlobalInternet.py)
# ============================================================================
COMPANY_GUIDELINES = """
GlobalInternet.py – Company Guidelines (for AI Customer Service)

CONTACT INFORMATION (always include in every response)
Email: deslandes78@gmail.com
Phone / WhatsApp: (509) 4738-5663 – available for WhatsApp chat, voice calls, and video calls
Website: https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/

COMPANY OVERVIEW
GlobalInternet.py is a software development company founded by Gesner Deslandes. We build custom Python-based software for clients worldwide, with a focus on AI, web applications, election systems, and automation. Our motto: “We provide tailored software solutions connecting the global market with our local expertise.”

CORE SERVICES & PRODUCTS
We offer the following software products (full source code included):
- AI Customer Service Suite – Automated text, email, and voice support.
- Haiti Online Voting Software – Secure, multi-language election platform.
- Business Intelligence Dashboards – Real-time analytics.
- AI Chatbots – Custom-trained for your business.
- School Management Systems – Student records, grades, attendance.
- Inventory & POS Systems – For retail and small businesses.
- Web Scrapers & Data Pipelines – Automated data extraction.
- Hospital Management Systems – EMR, billing, pharmacy.
- Drone Control Software – For Haitian drone operations.
- Language Learning Apps – English, French, Spanish, Portuguese, Chinese.
- Humanoid Robot Control Suite – For robotics and automation.
- And many more – Contact us for a full list.

PRICING & LICENSING
- One-time Full Package License: Prices range from $249 to $45,000 USD depending on the product. This includes the full source code, setup guide, and 1 year of email support.
- Monthly Subscription: Most software is also available on a monthly basis at $299 USD/month – includes updates and priority support.
- White-Label / Reseller License: Available for $2,999 USD – allows you to rebrand and resell the software.
- Agency / Enterprise License: $1,499 USD – for multiple projects or broader usage.

For any pricing inquiries, contact us at deslandes78@gmail.com.

PAYMENT METHODS
We accept the following payment methods:
- Bank Transfer – UNIBANK (US) account: 105-2016-16594727 (SWIFT: UNIBANKUS)
- SendWave – international transfer to phone (509) 4738-5663 (WhatsApp chat or video call for details)
- Prisme Transfer via Moncash (Digicel) – local Haitian transfer up to 100,000 HTG
- PayPal – available on request

DELIVERY & INSTALLATION
- Software is delivered by email as a downloadable ZIP file containing the full Python source code.
- A setup guide is included in the package.
- For an additional fee, we can provide remote installation assistance (Zoom/TeamViewer session).

SUPPORT POLICY
- Email support is included for 1 year after purchase (responses within 24 hours, Monday–Friday) – send all support requests to deslandes78@gmail.com.
- Phone support is available for urgent issues – call (509) 4738-5663 (also reachable via WhatsApp voice or video call).
- For monthly subscribers, support includes priority response and version updates.

REFUND POLICY
- Because software is delivered digitally, all sales are final. No refunds will be issued after the source code has been sent.
- We strongly encourage clients to test the live demo (available for most products) before purchasing.

CUSTOMER SERVICE HOURS
- Monday to Friday: 8:00 AM – 6:00 PM (Haiti time, GMT-4)
- Saturday: 9:00 AM – 1:00 PM
- Sunday: Closed (emergency calls only – WhatsApp video call available)

COMMUNICATION CHANNELS
- Email (Primary): deslandes78@gmail.com
- Phone / WhatsApp (Secondary): (509) 4738-5663 – supports WhatsApp chat, voice calls, and video calls
- Website: https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/
- Live demos: Provided upon request.

CUSTOM DEVELOPMENT
We also build tailored software solutions from scratch. If a client needs a unique application not listed, we provide a free consultation and a fixed-price quote. To discuss custom projects, email deslandes78@gmail.com or reach out via WhatsApp (text, voice, or video).

DATA SECURITY & PRIVACY
- All client data and source code are handled with strict confidentiality.
- We never share your software or personal information with third parties without explicit consent.
- Our website uses end-to-end encryption for all communications.

COMPANY TAGLINE (always include in AI responses)
“We provide tailored software solutions connecting the global market with our local expertise.”

FOOTER INFORMATION (always include in final replies)
Email: deslandes78@gmail.com
Phone / WhatsApp: (509) 4738-5663 (chat, voice, video)
Website: https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/
Founder: Gesner Deslandes, Engineer-in-Chief
"""

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="AI Customer Service Suite | GlobalInternet.py",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
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
        position: relative;
    }
    .main-title h1 {
        color: #ffd966;
    }
    .main-title p {
        color: #a0b0c0;
    }
    .profile-pic {
        position: absolute;
        top: 0;
        right: 0;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #ffd966;
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
        font-family: monospace;
        word-break: break-all;
    }
    .chat-message {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 10px;
        margin: 5px 0;
    }
    .email-log {
        background: rgba(0,255,200,0.05);
        border-left: 3px solid #00ebc7;
        padding: 10px;
        margin: 5px 0;
        font-family: monospace;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== LANGUAGE DICTIONARIES ==========
TEXTS = {
    "English": {
        "title": "🤖 AI Customer Service Suite",
        "subtitle": "Smart text, email, and voice support powered by your company guidelines",
        "intro_btn": "🎙️ Watch Introduction (AI Female Voice)",
        "intro_text": "Welcome to AI Customer Service Suite. This software helps companies automate customer support across text messages, emails, and phone/WhatsApp calls. You upload your company guidelines, and the AI answers every inquiry based on those policies. It works in English, French, and Spanish. You can connect your phone number via Twilio to answer WhatsApp chats and calls automatically. This tool saves time, improves response consistency, and works 24/7. The full source code is available for a one‑time payment. Small Business License is 499 US dollars. Agency or Enterprise License is 1,499 US dollars. White‑Label or Reseller License is 2,999 US dollars. Contact Gesner Deslandes at GlobalInternet.py to purchase. This software was built by Gesner Deslandes, Engineer‑in‑Chief at GlobalInternet.py.",
        "sidebar_title": "Company Setup",
        "guidelines_loaded": "✅ Company guidelines are pre‑loaded. AI will use them for all responses.",
        "no_guidelines": "⚠️ Guidelines are pre‑loaded. No need to upload.",
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
        "security_badge": "🔐 Secure API connection active",
        "lang": "Language",
        "guidelines_summary": "Guidelines Summary (first 500 chars):",
        "email_settings": "📧 Email Auto‑Reply (Gmail)",
        "email_address": "Your Gmail Address",
        "email_imap_server": "IMAP Server (default: imap.gmail.com)",
        "email_smtp_server": "SMTP Server (default: smtp.gmail.com)",
        "email_process_btn": "📬 Process Inbox & Auto‑Reply",
        "email_processing": "Processing unread emails...",
        "email_processed": "✅ Processed {} emails. Replies sent to {}.",
        "email_no_unread": "No unread emails found.",
        "email_error": "❌ Error processing emails: {}",
        "email_log_title": "📋 Email Processing Log",
        "email_company_tagline": "We provide tailored software solutions connecting global market with our local expertise."
    },
    "French": {
        "title": "🤖 Suite de service client IA",
        "subtitle": "Support textuel, email et vocal intelligent basé sur vos politiques",
        "intro_btn": "🎙️ Regarder l'introduction (voix IA féminine)",
        "intro_text": "Bienvenue dans la Suite de service client IA. Ce logiciel aide les entreprises à automatiser le support client par SMS, emails et appels téléphoniques/WhatsApp. Vous téléchargez vos politiques, et l'IA répond à chaque demande selon ces règles. Fonctionne en anglais, français et espagnol. Vous pouvez connecter votre numéro via Twilio pour répondre aux appels et chats WhatsApp automatiquement. Cet outil fait gagner du temps, améliore la cohérence et travaille 24/7. Le code source complet est disponible pour un paiement unique. La licence pour petites entreprises est de 499 dollars américains. La licence agence ou entreprise est de 1 499 dollars américains. La licence marque blanche ou revendeur est de 2 999 dollars américains. Contactez Gesner Deslandes chez GlobalInternet.py pour acheter. Ce logiciel a été construit par Gesner Deslandes, ingénieur en chef chez GlobalInternet.py.",
        "sidebar_title": "Configuration entreprise",
        "guidelines_loaded": "✅ Les politiques de l'entreprise sont pré‑chargées. L'IA les utilisera pour toutes les réponses.",
        "no_guidelines": "⚠️ Les politiques sont pré‑chargées. Pas besoin de télécharger.",
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
        "security_badge": "🔐 Connexion API sécurisée active",
        "lang": "Langue",
        "guidelines_summary": "Résumé des politiques (500 premiers caractères) :",
        "email_settings": "📧 Réponse automatique par email (Gmail)",
        "email_address": "Votre adresse Gmail",
        "email_imap_server": "Serveur IMAP (défaut : imap.gmail.com)",
        "email_smtp_server": "Serveur SMTP (défaut : smtp.gmail.com)",
        "email_process_btn": "📬 Traiter la boîte de réception et répondre",
        "email_processing": "Traitement des emails non lus...",
        "email_processed": "✅ {} emails traités. Réponses envoyées à {}.",
        "email_no_unread": "Aucun email non lu trouvé.",
        "email_error": "❌ Erreur lors du traitement : {}",
        "email_log_title": "📋 Journal des emails traités",
        "email_company_tagline": "Nous fournissons des solutions logicielles sur mesure reliant le marché mondial à notre expertise locale."
    },
    "Spanish": {
        "title": "🤖 Suite de servicio al cliente IA",
        "subtitle": "Soporte inteligente por texto, email y voz basado en sus políticas",
        "intro_btn": "🎙️ Ver introducción (voz IA femenina)",
        "intro_text": "Bienvenido a la Suite de servicio al cliente IA. Este software ayuda a las empresas a automatizar el soporte al cliente mediante mensajes de texto, correos electrónicos y llamadas telefónicas/WhatsApp. Usted sube sus políticas y la IA responde cada consulta según esas reglas. Funciona en inglés, francés y español. Puede conectar su número de teléfono a través de Twilio para responder chats y llamadas de WhatsApp automáticamente. Esta herramienta ahorra tiempo, mejora la consistencia y trabaja 24/7. El código fuente completo está disponible por un pago único. La licencia para pequeñas empresas es de 499 dólares estadounidenses. La licencia para agencia o empresa es de 1.499 dólares estadounidenses. La licencia de marca blanca o reventa es de 2.999 dólares estadounidenses. Contacte a Gesner Deslandes en GlobalInternet.py para comprar. Este software fue construido por Gesner Deslandes, ingeniero jefe de GlobalInternet.py.",
        "sidebar_title": "Configuración de la empresa",
        "guidelines_loaded": "✅ Las políticas de la empresa están pre‑cargadas. La IA las usará para todas las respuestas.",
        "no_guidelines": "⚠️ Las políticas están pre‑cargadas. No es necesario subir archivos.",
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
        "security_badge": "🔐 Conexión API segura activa",
        "lang": "Idioma",
        "guidelines_summary": "Resumen de políticas (primeros 500 caracteres):",
        "email_settings": "📧 Respuesta automática por email (Gmail)",
        "email_address": "Su dirección de Gmail",
        "email_imap_server": "Servidor IMAP (por defecto: imap.gmail.com)",
        "email_smtp_server": "Servidor SMTP (por defecto: smtp.gmail.com)",
        "email_process_btn": "📬 Procesar bandeja de entrada y responder",
        "email_processing": "Procesando correos no leídos...",
        "email_processed": "✅ {} correos procesados. Respuestas enviadas a {}.",
        "email_no_unread": "No se encontraron correos no leídos.",
        "email_error": "❌ Error al procesar correos: {}",
        "email_log_title": "📋 Registro de correos procesados",
        "email_company_tagline": "Proporcionamos soluciones de software a medida que conectan el mercado global con nuestra experiencia local."
    }
}

# ========== VOICE MAPPINGS ==========
FEMALE_VOICE_MAP = {
    "English": "en-US-JennyNeural",
    "French": "fr-FR-DeniseNeural",
    "Spanish": "es-ES-ElviraNeural"
}

MALE_VOICE_MAP = {
    "English": "en-US-ChristopherNeural",
    "French": "fr-FR-HenriNeural",
    "Spanish": "es-ES-AlvaroNeural"
}

# ========== MALE VOICE INTRO TEXT ==========
MALE_INTRO_TEXT = {
    "English": "Hello, this is Gesner Deslandes from GlobalInternet.py. The AI Customer Service Suite automates customer support using your company guidelines. It answers text messages, emails, and phone calls in English, French, or Spanish. You can connect your phone via Twilio for WhatsApp and voice. Full source code is available. Small Business License 499 dollars. Agency License 1499 dollars. White‑Label License 2999 dollars. Contact us at (509) 4738 5663 or deslandes78@gmail.com. Visit GlobalInternet.py to purchase.",
    "French": "Bonjour, ici Gesner Deslandes de GlobalInternet.py. La Suite de service client IA automatise le support client avec vos propres politiques. Elle répond par SMS, email et appel en anglais, français ou espagnol. Connectez votre numéro via Twilio pour WhatsApp et la voix. Code source disponible. Licence petite entreprise 499 dollars. Licence agence 1499 dollars. Licence marque blanche 2999 dollars. Contactez‑nous au (509) 4738 5663 ou à deslandes78@gmail.com. Visitez GlobalInternet.py pour acheter.",
    "Spanish": "Hola, soy Gesner Deslandes de GlobalInternet.py. La Suite de servicio al cliente IA automatiza el soporte usando sus políticas. Responde mensajes, correos y llamadas en inglés, francés o español. Conecte su número vía Twilio para WhatsApp y voz. Código fuente disponible. Licencia pequeña empresa 499 dólares. Licencia agencia 1499 dólares. Licencia marca blanca 2999 dólares. Contáctenos al (509) 4738 5663 o a deslandes78@gmail.com. Visite GlobalInternet.py para comprar."
}

# ========== EXTRACT TEXT FROM UPLOADED FILE (kept for reference, but not used) ==========
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

# ========== AI RESPONSE FUNCTION ==========
def get_ai_response(question, guidelines, lang):
    if not guidelines:
        return "Please upload your company guidelines first. / Veuillez d'abord télécharger vos politiques. / Por favor, cargue primero sus políticas."
    
    tagline = TEXTS[lang]["email_company_tagline"]
    
    system_prompt = f"""You are an AI customer service agent for a company. Answer the customer's question based ONLY on the following company guidelines. Be polite, helpful, and concise. If the question cannot be answered from the guidelines, say "I cannot find that information in our guidelines. Please contact a human agent." 
Always include this company tagline somewhere in your response: "{tagline}"
Respond in {lang}.

Guidelines:
{guidelines[:4000]}

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

# ========== TEXT TO SPEECH ==========
async def text_to_speech(text, voice, output_path):
    comm = edge_tts.Communicate(text, voice)
    await comm.save(output_path)

def generate_audio(text, lang, voice_type="female"):
    if voice_type == "male":
        voice = MALE_VOICE_MAP.get(lang, "en-US-ChristopherNeural")
    else:
        voice = FEMALE_VOICE_MAP.get(lang, "en-US-JennyNeural")
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

# ========== EMAIL AUTO‑REPLY FUNCTIONS (using flat secret) ==========
def get_email_body(msg):
    """Extract plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode("utf-8", errors="ignore")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                return re.sub(r'<[^>]+>', '', html)
    else:
        return msg.get_payload(decode=True).decode("utf-8", errors="ignore")
    return ""

def process_emails(gmail_user, guidelines, lang, imap_server="imap.gmail.com", smtp_server="smtp.gmail.com"):
    """
    Connect to Gmail, fetch unread emails, generate AI replies, and send them.
    Uses the app password stored in st.secrets["EMAIL_PASSWORD"] (flat key).
    """
    log = []
    try:
        # Get password from flat secret (more robust)
        gmail_password = st.secrets["EMAIL_PASSWORD"]
        
        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(gmail_user, gmail_password)
        imap.select("INBOX")
        
        status, messages = imap.search(None, "UNSEEN")
        if status != "OK":
            raise Exception("Failed to search for unread emails.")
        
        email_ids = messages[0].split()
        if not email_ids:
            return [], "No unread emails found."
        
        processed_count = 0
        replied_to = []
        
        for eid in email_ids:
            status, msg_data = imap.fetch(eid, "(RFC822)")
            if status != "OK":
                continue
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            subject = msg.get("Subject", "No Subject")
            from_addr = msg.get("From")
            body = get_email_body(msg)
            
            reply_text = get_ai_response(body, guidelines, lang)
            
            smtp = smtplib.SMTP_SSL(smtp_server, 465)
            smtp.login(gmail_user, gmail_password)
            
            reply_msg = MIMEMultipart()
            reply_msg["From"] = gmail_user
            reply_msg["To"] = from_addr
            reply_msg["Subject"] = f"Re: {subject}"
            reply_msg.attach(MIMEText(reply_text, "plain", "utf-8"))
            
            smtp.send_message(reply_msg)
            smtp.quit()
            
            processed_count += 1
            replied_to.append(from_addr)
            log.append(f"Replied to {from_addr} about '{subject}'")
        
        imap.close()
        imap.logout()
        
        return log, f"Processed {processed_count} emails. Replied to: {', '.join(replied_to)}"
    
    except Exception as e:
        return log, f"Error: {str(e)}"

# ========== INIT SESSION STATE ==========
if "guidelines_text" not in st.session_state:
    st.session_state.guidelines_text = COMPANY_GUIDELINES
if "lang" not in st.session_state:
    st.session_state.lang = "English"
if "twilio_sid" not in st.session_state:
    st.session_state.twilio_sid = ""
if "twilio_auth" not in st.session_state:
    st.session_state.twilio_auth = ""
if "twilio_phone" not in st.session_state:
    st.session_state.twilio_phone = ""
if "email_address" not in st.session_state:
    st.session_state.email_address = "deslandes78@gmail.com"
if "email_imap_server" not in st.session_state:
    st.session_state.email_imap_server = "imap.gmail.com"
if "email_smtp_server" not in st.session_state:
    st.session_state.email_smtp_server = "smtp.gmail.com"
if "email_log" not in st.session_state:
    st.session_state.email_log = []

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
    st.markdown(f"### 🛡️ Global Security Shield")
    st.markdown(f'<div class="security-badge">{texts["security_badge"]}</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Male Voice Button
    st.markdown("### 🎙️ AI Voice for Social Media")
    male_btn = st.button("🎙️ AI Male Voice – Describe Software for Social Media", use_container_width=True)
    if male_btn:
        with st.spinner("Generating male voice description..."):
            audio_bytes = generate_audio(MALE_INTRO_TEXT[st.session_state.lang], st.session_state.lang, voice_type="male")
            st.audio(audio_bytes, format="audio/mp3")
            st.success("Male voice description played. You can share this audio on social media.")
    st.markdown("---")
    
    st.subheader(texts["sidebar_title"])
    st.success(texts["guidelines_loaded"])
    with st.expander(texts["guidelines_summary"]):
        st.write(st.session_state.guidelines_text[:500] + "...")
    
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
    
    # Email Auto‑Reply Section – NO PASSWORD FIELD
    st.markdown(f"### {texts['email_settings']}")
    email_address = st.text_input(texts["email_address"], value=st.session_state.email_address)
    st.info("🔒 Password stored in secrets (EMAIL_PASSWORD).")
    imap_server = st.text_input("IMAP Server", value=st.session_state.email_imap_server)
    smtp_server = st.text_input("SMTP Server", value=st.session_state.email_smtp_server)
    if st.button("Save Email Settings", use_container_width=True):
        st.session_state.email_address = email_address
        st.session_state.email_imap_server = imap_server
        st.session_state.email_smtp_server = smtp_server
        st.success("Email settings saved.")
    
    st.markdown("---")
    st.markdown("Built by **Gesner Deslandes**, Engineer-in-Chief")
    st.markdown("📞 (509) 4738 5663")
    st.markdown("✉️ deslandes78@gmail.com")
    st.markdown("---")
    st.caption(texts["footer"])

# ========== MAIN PAGE ==========
profile_col, title_col = st.columns([1, 9])
with profile_col:
    st.image("https://raw.githubusercontent.com/Deslandes1/ai-customer-service-suite/main/Gesner%20Deslandes.png", width=70)
with title_col:
    st.markdown(f'<div class="main-title"><h1>{texts["title"]}</h1><p>{texts["subtitle"]}</p></div>', unsafe_allow_html=True)

# Female Voice Intro
if st.button(texts["intro_btn"], use_container_width=True):
    with st.spinner("Generating voice introduction..."):
        audio = generate_audio(texts["intro_text"], st.session_state.lang, voice_type="female")
        st.audio(audio, format="audio/mp3")
        st.success("Introduction played. You can listen again if needed.")

st.markdown("---")

if "GROQ_API_KEY" not in st.secrets:
    st.error(texts["api_key_warning"])
else:
    st.subheader(texts["customer_chat"])
    
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
            
            if customer_email:
                st.info(f"📧 A copy of this response would be sent to {customer_email}")

st.markdown("---")

# ========== EMAIL AUTO‑REPLY SECTION ==========
st.subheader("📬 Automated Email Reply")
st.write("Connect your Gmail account and click the button below to process all unread emails. The AI will generate replies based on your guidelines and send them automatically.")

col1, col2 = st.columns([2,1])
with col1:
    process_btn = st.button(texts["email_process_btn"], use_container_width=True)
with col2:
    st.write("")

if process_btn:
    if not st.session_state.guidelines_text:
        st.warning(texts["no_guidelines"])
    elif not st.session_state.email_address:
        st.warning("Veuillez entrer votre adresse Gmail dans la barre latérale.")
    else:
        with st.spinner(texts["email_processing"]):
            log, result = process_emails(
                st.session_state.email_address,
                st.session_state.guidelines_text,
                st.session_state.lang,
                st.session_state.email_imap_server,
                st.session_state.email_smtp_server
            )
        if "Error" in result:
            st.error(texts["email_error"].format(result))
        elif "No unread" in result:
            st.info(texts["email_no_unread"])
        else:
            st.success(texts["email_processed"].format(len(log), ", ".join([entry.split(" ")[2] for entry in log])))
            st.session_state.email_log = log
            st.balloons()

if st.session_state.email_log:
    st.markdown(f"### {texts['email_log_title']}")
    for entry in st.session_state.email_log:
        st.markdown(f'<div class="email-log">📨 {entry}</div>', unsafe_allow_html=True)

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
