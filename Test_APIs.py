import streamlit as st
import asyncio
from openai import AsyncOpenAI
from google import genai
import anthropic

st.set_page_config(page_title="Debug APIs", layout="wide")
st.title("🧪 Painel de Diagnóstico de APIs")
st.markdown("Teste cada chave individualmente para descobrir quem está bloqueando a conexão.")

# ==========================================
# LEITURA DAS CHAVES
# ==========================================
api_gpt = st.secrets.get("OPENAI_API_KEY", "")
api_gemini = st.secrets.get("GEMINI_API_KEY", "")
api_claude = st.secrets.get("ANTHROPIC_API_KEY", "")
api_deepseek = st.secrets.get("DEEPSEEK_API_KEY", "")
api_grok = st.secrets.get("XAI_API_KEY", "")

st.write("### Status Local das Chaves (secrets.toml):")
col1, col2, col3, col4, col5 = st.columns(5)
col1.info(f"GPT: {'✅ Encontrada' if api_gpt else '❌ Vazia'}")
col2.info(f"Gemini: {'✅ Encontrada' if api_gemini else '❌ Vazia'}")
col3.info(f"Claude: {'✅ Encontrada' if api_claude else '❌ Vazia'}")
col4.info(f"DeepSeek: {'✅ Encontrada' if api_deepseek else '❌ Vazia'}")
col5.info(f"Grok: {'✅ Encontrada' if api_grok else '❌ Vazia'}")

st.write("---")

# ==========================================
# FUNÇÕES DE TESTE ISOLADAS
# ==========================================
async def testar_gpt():
    try:
        cliente = AsyncOpenAI(api_key=api_gpt)
        resp = await cliente.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": "Diga apenas 'Olá, GPT funcionando!' e nada mais."}]
        )
        return resp.choices[0].message.content
    except Exception as e: return f"ERRO: {e}"

async def testar_gemini():
    try:
        cliente = genai.Client(api_key=api_gemini)
        resp = await cliente.aio.models.generate_content(
            model='gemini-2.5-flash', contents="Diga apenas 'Olá, Gemini funcionando!' e nada mais."
        )
        return resp.text
    except Exception as e: return f"ERRO: {e}"

async def testar_claude():
    try:
        cliente = anthropic.AsyncAnthropic(api_key=api_claude)
        resp = await cliente.messages.create(
            model="claude-3-5-sonnet-20241022", max_tokens=100,
            messages=[{"role": "user", "content": "Diga apenas 'Olá, Claude funcionando!' e nada mais."}]
        )
        return resp.content[0].text
    except Exception as e: return f"ERRO: {e}"

async def testar_deepseek():
    try:
        cliente = AsyncOpenAI(api_key=api_deepseek, base_url="https://api.deepseek.com")
        resp = await cliente.chat.completions.create(
            model="deepseek-chat", messages=[{"role": "user", "content": "Diga apenas 'Olá, DeepSeek funcionando!' e nada mais."}]
        )
        return resp.choices[0].message.content
    except Exception as e: return f"ERRO: {e}"

async def testar_grok():
    try:
        cliente = AsyncOpenAI(api_key=api_grok, base_url="https://api.x.ai/v1")
        resp = await cliente.chat.completions.create(
            model="grok-2-latest", messages=[{"role": "user", "content": "Diga apenas 'Olá, Grok funcionando!' e nada mais."}]
        )
        return resp.choices[0].message.content
    except Exception as e: return f"ERRO: {e}"

# ==========================================
# INTERFACE DE TESTE
# ==========================================
st.write("### Execute os testes:")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    if st.button("🚀 Testar ChatGPT", use_container_width=True):
        with st.spinner("Chamando..."):
            resultado = asyncio.run(testar_gpt())
            if "ERRO" in resultado: st.error(resultado)
            else: st.success(resultado)

with c2:
    if st.button("🚀 Testar Gemini", use_container_width=True):
        with st.spinner("Chamando..."):
            resultado = asyncio.run(testar_gemini())
            if "ERRO" in resultado: st.error(resultado)
            else: st.success(resultado)

with c3:
    if st.button("🚀 Testar Claude", use_container_width=True):
        with st.spinner("Chamando..."):
            resultado = asyncio.run(testar_claude())
            if "ERRO" in resultado: st.error(resultado)
            else: st.success(resultado)

with c4:
    if st.button("🚀 Testar DeepSeek", use_container_width=True):
        with st.spinner("Chamando..."):
            resultado = asyncio.run(testar_deepseek())
            if "ERRO" in resultado: st.error(resultado)
            else: st.success(resultado)

with c5:
    if st.button("🚀 Testar Grok", use_container_width=True):
        with st.spinner("Chamando..."):
            resultado = asyncio.run(testar_grok())
            if "ERRO" in resultado: st.error(resultado)
            else: st.success(resultado)