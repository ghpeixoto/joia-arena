import streamlit as st
import time

st.set_page_config(page_title="Claude Clone", layout="wide", initial_sidebar_state="collapsed")

# CSS AGRESSIVO PARA CORRIGIR OS BOTÕES E O LAYOUT DO STREAMLIT
st.markdown("""
    <style>
    /* Reset Geral */
    .stApp { background-color: #242424; color: #ececec; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    footer {visibility: hidden;}
    
    /* Tipografia Claude */
    .serif-title { font-family: "Georgia", serif; font-weight: 400; color: #e0dacc; }
    .claude-star { color: #d97757; font-size: 1.2em; }
    
    /* Container Centralizado para Onboarding */
    .onboarding-container { max-width: 640px; margin: 0 auto; padding-top: 10vh; }
    
    /* =========================================
       CORREÇÃO DO MENU LATERAL (Print 4)
       ========================================= */
    div[data-testid="stSidebar"] { background-color: #1e1e1e !important; border-right: 1px solid #333 !important; }
    
    /* Força os botões da Sidebar a serem invisíveis e alinhados à esquerda */
    div[data-testid="stSidebar"] div.stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: #e5e7eb !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        box-shadow: none !important;
        border-radius: 6px !important;
    }
    div[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #2d2d2d !important;
    }
    
    /* =========================================
       CORREÇÃO DOS BOTÕES DA TELA PRINCIPAL
       ========================================= */
    /* Botões Padrão (Continuar, Vamos lá) */
    div.stButton > button { 
        background-color: #ececec; color: #1e1e1e; border: none; border-radius: 8px; font-weight: 500; padding: 10px 20px; width: 100%; transition: 0.2s; 
    }
    div.stButton > button:hover { background-color: #ffffff; }
    
    /* Input de Texto (Nome) */
    div[data-baseweb="input"] { background-color: transparent; border: 1px solid #555; border-radius: 12px; }
    div[data-baseweb="input"] > input { color: #ececec; padding: 12px; font-size: 16px; }
    
    /* Saudação Central */
    .main-greeting { text-align: center; margin-top: 15vh; margin-bottom: 40px; font-size: 2.5rem;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# MÁQUINA DE ESTADO
# ==========================================
if 'fluxo' not in st.session_state:
    st.session_state.fluxo = 'intro' # Pulei os termos para ir direto ao fluxo principal
if 'nome_usuario' not in st.session_state:
    st.session_state.nome_usuario = ""

def avancar_fluxo(proxima_etapa):
    st.session_state.fluxo = proxima_etapa

# ==========================================
# ETAPA 1: APRESENTAÇÃO
# ==========================================
if st.session_state.fluxo == 'intro':
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div class='onboarding-container'>", unsafe_allow_html=True)
        st.markdown("<h1 class='serif-title'><span class='claude-star'>✺</span><br>Olá, eu sou o Claude.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: #d1d5db; margin-bottom: 30px;'>Sou seu assistente de IA para trabalhar, imaginar e pensar profundamente.</p>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='margin-bottom: 20px;'><b>🕊️ Curioso? É só perguntar</b><br><span style='color: #9ca3af; font-size: 0.9em;'>Converse comigo sobre qualquer assunto. Proteções mantêm nosso chat seguro.</span></div>
        <div style='margin-bottom: 20px;'><b>🛡️ Chats sem anúncios</b><br><span style='color: #9ca3af; font-size: 0.9em;'>Não vou mostrar anúncios para você. Meu foco é ser genuinamente útil.</span></div>
        <div style='margin-bottom: 30px;'><b>👍 Você pode melhorar o Claude</b><br><span style='color: #9ca3af; font-size: 0.9em;'>Usamos suas conversas para treinar o Claude.</span></div>
        """, unsafe_allow_html=True)
        
        st.toggle("Ajudar a Melhorar o Claude", value=True)
        st.write("")
        c1, c2 = st.columns([1, 3])
        with c1: st.button("Entendi", on_click=avancar_fluxo, args=('nome',))
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# ETAPA 2: NOME
# ==========================================
elif st.session_state.fluxo == 'nome':
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div class='onboarding-container'>", unsafe_allow_html=True)
        st.markdown("<h1 class='serif-title'><span class='claude-star'>✺</span><br>Antes de começarmos, como devo chamá-lo?</h1><br>", unsafe_allow_html=True)
        
        nome_input = st.text_input("", placeholder="Digite seu nome", label_visibility="collapsed")
        if nome_input:
            time.sleep(0.2)
            st.session_state.nome_usuario = nome_input
            avancar_fluxo('topicos')
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# ETAPA 3: TÓPICOS
# ==========================================
elif st.session_state.fluxo == 'topicos':
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div class='onboarding-container'>", unsafe_allow_html=True)
        st.markdown(f"<h1 class='serif-title'><span class='claude-star'>✺</span><br>Do que você gosta, {st.session_state.nome_usuario}? Escolha três tópicos.</h1><br>", unsafe_allow_html=True)
        
        # Botões escuros customizados inline para os tópicos
        st.markdown("""
        <style>
        .topic-btn { background-color: #2b2b2b; color: #ececec; border: 1px solid #444; border-radius: 8px; padding: 10px 15px; width: 100%; text-align: left; margin-bottom: 10px; cursor: pointer;}
        .topic-btn:hover { background-color: #383838; }
        </style>
        <button class='topic-btn'>&lt;/&gt; Programação e desenvolvimento</button>
        <button class='topic-btn'>✏️ Redação e criação de conteúdo</button>
        <button class='topic-btn'>🎨 Design e criatividade</button>
        """, unsafe_allow_html=True)
        
        st.write("")
        c1, c2 = st.columns([1, 3])
        with c1: st.button("Vamos lá", on_click=avancar_fluxo, args=('chat',))
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# ETAPA 4: TELA PRINCIPAL
# ==========================================
elif st.session_state.fluxo == 'chat':
    with st.sidebar:
        st.markdown("<h2 class='serif-title' style='margin-top:0;'>Claude</h2>", unsafe_allow_html=True)
        st.button("➕ Novo bate-papo")
        st.button("🔍 Procurar")
        st.write("---")
        st.button("💬 Conversas")
        st.button("🗂️ Projetos")
        st.button("✨ Artefatos")
        st.button("</> Código")
        st.markdown("<br><p style='text-align: center; color: #6b7280; font-size: 12px;'>Seus chats aparecerão aqui</p>", unsafe_allow_html=True)

    st.markdown(f"<h1 class='serif-title main-greeting'><span class='claude-star'>✺</span> Boa tarde, {st.session_state.nome_usuario}</h1>", unsafe_allow_html=True)
    
    prompt = st.chat_input("Como posso ajudar você hoje?")
    if prompt:
        st.success("Fluxo concluído! Aqui entrará a lógica de chat.")