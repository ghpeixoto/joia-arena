import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3
import asyncio
import re
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI(title="JoIA Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cliente_openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
cliente_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. MEMÓRIA E APRENDIZADO DIÁRIO
# ==========================================
def save_message(chat_id: str, role: str, content: str, image_b64: str = None):
    try:
        conn = sqlite3.connect('moreprod_db.sqlite')
        c = conn.cursor()
        c.execute("INSERT INTO chat_history (chat_id, role, content, image_b64) VALUES (?, ?, ?, ?)", (chat_id, role, content, image_b64))
        conn.commit()
        conn.close()
    except Exception as e: print(f"Erro ao salvar: {e}")

def load_context(chat_id: str, limit: int = 4):
    try:
        conn = sqlite3.connect('moreprod_db.sqlite')
        c = conn.cursor()
        c.execute("SELECT role, content FROM chat_history WHERE chat_id = ? ORDER BY id DESC LIMIT ?", (chat_id, limit))
        rows = c.fetchall()
        conn.close()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
    except: return []

def carregar_sabedoria_diaria():
    try:
        conn = sqlite3.connect('moreprod_db.sqlite')
        c = conn.cursor()
        c.execute("SELECT content FROM chat_history WHERE role = 'assistant' AND content LIKE '%Certeza: 98%%' OR content LIKE '%Certeza: 99%%' OR content LIKE '%Certeza: 100%%' ORDER BY id DESC LIMIT 2")
        rows = c.fetchall()
        conn.close()
        if not rows: return "Nenhum aprendizado prévio armazenado."
        return "\n---\n".join([r[0] for r in rows])
    except: return "Banco de dados iniciando..."

# ==========================================
# 2. PROMPTS DE STRESS TEST E ALTA PERFORMANCE
# ==========================================
PROMPT_BASE = """
És um Engenheiro de Software e Arquiteto de Dados de Elite na Arena JoIA.
A tua base de conhecimento prévia (Sabedoria): {sabedoria}

TENS DE AGIR SOB STRESS TOTAL:
1. Analisa o pedido profundamente. Se envolver bases de dados pesadas (ex: DAX para 30 milhões de linhas), pensa obrigatoriamente em engine VertiPaq, alocação de memória e eliminação de transições de contexto desnecessárias.
2. Desenvolve a solução mais robusta, performática e à prova de falhas logo na primeira tentativa.
3. Não uses abordagens genéricas. Otimiza para escala empresarial.

Retorna APENAS o código puro nesta fase inicial, sem comentários ou explicações.
"""

PROMPT_AUDITOR = """
És o Auditor Implacável da Arena JoIA. O teu objetivo é destruir, criticar e reconstruir o código até atingir a perfeição (98%+ de certeza).

ESTADO ATUAL DA BATALHA:
O Teu Código (Versão Anterior):
{meu_codigo}

O Código do Oponente:
{outro_codigo}

PROTOCOLO DE STRESS TEST (Executa mentalmente antes de responder):
1. VULNERABILIDADES: Encontra falhas de performance, gargalos de memória, iterações excessivas (ex: CALCULATE ou FILTER mal aplicados) no código do oponente e no teu.
2. COMPARAÇÃO CRUZADA: Extrai a melhor lógica matemática/sintática de ambos os códigos.
3. EVOLUÇÃO: Cria uma Versão 2.0 que esmague as versões anteriores em tempo de execução e eficiência.

DIRETRIZES DE PONTUAÇÃO (CERTEZA):
- 50-70%: Código funcional, mas perigoso para grandes volumes de dados.
- 71-90%: Código otimizado, mas ainda com ligeira margem para refatorização.
- 91-97%: Nível de produção, altamente performático.
- 98-100%: Perfeição absoluta. Código definitivo e imbatível sob stress extremo.

RETORNA EXATAMENTE NESTE FORMATO OBRIGATÓRIO (sem markdown de bloco de código a envolver as tags):
[CODIGO]
<escreve a tua versão evoluída e final do código aqui>
[/CODIGO]
[CERTEZA]<numero inteiro de 0 a 100>[/CERTEZA]
[ANALISE]<Explicação profunda: o que alteraste em relação ao oponente, que gargalo resolveste e como garantiste performance extrema.>[/ANALISE]
"""

def extrair_debate(texto: str):
    try:
        codigo = re.search(r'\[CODIGO\](.*?)\[/CODIGO\]', texto, re.DOTALL | re.IGNORECASE).group(1).strip()
        certeza = int(re.search(r'\[CERTEZA\](\d+)\[/CERTEZA\]', texto, re.IGNORECASE).group(1))
        analise = re.search(r'\[ANALISE\](.*?)\[/ANALISE\]', texto, re.DOTALL | re.IGNORECASE).group(1).strip()
        codigo = re.sub(r'^```[a-z]*\n', '', codigo, flags=re.IGNORECASE | re.MULTILINE)
        codigo = re.sub(r'```$', '', codigo).strip()
        return {"codigo": codigo, "certeza": certeza, "analise": analise}
    except Exception as e: 
        print(f"Erro no parse: {e} | Texto original: {texto[:100]}...")
        return None

# ==========================================
# 3. ENDPOINT STREAMING (A MÁGICA DO TEMPO REAL)
# ==========================================
class RequestChat(BaseModel):
    chat_id: str
    mensagem: str
    imagem_b64: Optional[str] = None

@app.post("/api/chat")
async def processar_mensagem_stream(req: RequestChat):
    save_message(req.chat_id, "user", req.mensagem, req.imagem_b64)
    contexto = load_context(req.chat_id)

    async def gerador_arena():
        prompt_sistema = PROMPT_BASE.format(sabedoria=carregar_sabedoria_diaria())
        
        msg_gpt = [{"role": "system", "content": prompt_sistema}]
        for m in contexto: msg_gpt.append({"role": m["role"] if m["role"] == "user" else "assistant", "content": m["content"]})
        if req.imagem_b64: msg_gpt.append({"role": "user", "content": [{"type": "text", "text": req.mensagem}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{req.imagem_b64}"}}]})
        else: msg_gpt.append({"role": "user", "content": req.mensagem})

        contexto_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in contexto])
        msg_gemini = [f"INSTRUÇÕES:\n{prompt_sistema}\n\nCONTEXTO:\n{contexto_str}\n\nNOVO PEDIDO:\n{req.mensagem}"]

        try:
            # Envia Placar 0
            yield f"data: {json.dumps({'type': 'progress', 'rodada': 0, 'gpt': 0, 'gemini': 0})}\n\n"

            r_gpt = await cliente_openai.chat.completions.create(model="gpt-4o", temperature=0.0, messages=msg_gpt)
            cod_gpt = r_gpt.choices[0].message.content.strip()
            r_gem = await cliente_gemini.aio.models.generate_content(model='gemini-2.5-flash', contents=msg_gemini, config=types.GenerateContentConfig(temperature=0.0))
            cod_gem = r_gem.text.strip()
        except Exception as e:
            yield f"data: {json.dumps({'type': 'final', 'resposta': f'Erro: {str(e)}'})}\n\n"
            return

        dados_gpt, dados_gem = {"certeza": 50, "analise": "Análise profunda inicial..."}, {"certeza": 50, "analise": "Análise profunda inicial..."}
        
        # Envia Placar Inicial
        yield f"data: {json.dumps({'type': 'progress', 'rodada': 1, 'gpt': 50, 'gemini': 50})}\n\n"

        rodadas_feitas = 1
        for rodada in range(1, 13):
            rodadas_feitas = rodada
            
            # NOVA REGRA DA ARENA: Só param se AMBOS tiverem 98%+ de certeza.
            if dados_gpt['certeza'] >= 98 and dados_gem['certeza'] >= 98:
                break

            try:
                p_gpt = PROMPT_AUDITOR.format(meu_codigo=cod_gpt, outro_codigo=cod_gem)
                p_gem = PROMPT_AUDITOR.format(meu_codigo=cod_gem, outro_codigo=cod_gpt)
                
                r_gpt_aud = await cliente_openai.chat.completions.create(model="gpt-4o", temperature=0.0, messages=[{"role": "system", "content": "Auditor GPT"}, {"role": "user", "content": p_gpt}])
                r_gem_aud = await cliente_gemini.aio.models.generate_content(model='gemini-2.5-flash', contents=[f"Auditor Gemini.\n\n{p_gem}"], config=types.GenerateContentConfig(temperature=0.0))
                
                n_gpt = extrair_debate(r_gpt_aud.choices[0].message.content.strip())
                n_gem = extrair_debate(r_gem_aud.text.strip())
                
                if n_gpt: cod_gpt, dados_gpt = n_gpt['codigo'], n_gpt
                if n_gem: cod_gem, dados_gem = n_gem['codigo'], n_gem
                
                # ENVIA PLACAR AO VIVO PARA O REACT
                yield f"data: {json.dumps({'type': 'progress', 'rodada': rodada+1, 'gpt': dados_gpt['certeza'], 'gemini': dados_gem['certeza']})}\n\n"
                
                await asyncio.sleep(0.5)
            except Exception as e: 
                print(f"Erro na rodada {rodada}: {e}")
                break

        # Define Vencedor e Perdedor
        if dados_gpt['certeza'] >= dados_gem['certeza']:
            venc_nome, cod_venc, dados_venc = "GPT-4o", cod_gpt, dados_gpt
            perd_nome, cod_perd, dados_perd = "Gemini 2.5", cod_gem, dados_gem
        else:
            venc_nome, cod_venc, dados_venc = "Gemini 2.5", cod_gem, dados_gem
            perd_nome, cod_perd, dados_perd = "GPT-4o", cod_gpt, dados_gpt

        resposta_final = (
            f"### 🏆 PRIMEIRA OPÇÃO ({venc_nome} - Vencedor)\n"
            f"**Certeza Técnica: {dados_venc['certeza']}%**\n\n"
            f"```\n{cod_venc}\n```\n"
            f"*📝 Explicação da Evolução:* {dados_venc['analise']}\n\n"
            f"---\n\n"
            f"### 🥈 SEGUNDA OPÇÃO ({perd_nome})\n"
            f"**Certeza Técnica: {dados_perd['certeza']}%**\n\n"
            f"```\n{cod_perd}\n```\n"
            f"*📝 Explicação da Evolução:* {dados_perd['analise']}"
        )

        save_message(req.chat_id, "assistant", resposta_final)
        
        # Envia Resultado Final
        yield f"data: {json.dumps({'type': 'final', 'resposta': resposta_final})}\n\n"

    return StreamingResponse(gerador_arena(), media_type="text/event-stream")

@app.get("/api/historico/{chat_id}")
def listar_historico(chat_id: str):
    conn = sqlite3.connect('moreprod_db.sqlite')
    c = conn.cursor()
    c.execute("SELECT role, content, image_b64 FROM chat_history WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
    rows = c.fetchall()
    conn.close()
    return {"messages": [{"role": r[0], "content": r[1], "image_b64": r[2]} for r in rows]}

@app.get("/api/chats")
def listar_sidebar():
    """Busca todas as conversas e garante títulos únicos e limpos na barra lateral"""
    try:
        conn = sqlite3.connect('moreprod_db.sqlite')
        c = conn.cursor()
        
        # Query 100% à prova de falhas (usa o rowid nativo do SQLite para não misturar os chats)
        c.execute('''
            SELECT h.chat_id, h.content
            FROM chat_history h
            INNER JOIN (
                SELECT chat_id, MIN(rowid) as min_id
                FROM chat_history
                WHERE role = 'user'
                GROUP BY chat_id
            ) first_msgs ON h.chat_id = first_msgs.chat_id AND h.rowid = first_msgs.min_id
            ORDER BY h.rowid DESC
        ''')
        rows = c.fetchall()
        conn.close()
        
        chats_formatados = []
        nomes_usados = {}
        
        for r in rows:
            chat_id = r[0]
            texto_original = r[1] if r[1] else "Nova Conversa"
            
            # 1. Limpa quebras de linha e espaços extras
            titulo_limpo = " ".join(texto_original.split())
            
            # 2. Corta o título se for muito longo (para caber no menu lateral)
            if len(titulo_limpo) > 28: 
                titulo_limpo = titulo_limpo[:28] + "..."
                
            # 3. Lógica Anti-Duplicação (Se testar a mesma pergunta várias vezes)
            if titulo_limpo in nomes_usados:
                nomes_usados[titulo_limpo] += 1
                titulo_final = f"{titulo_limpo} ({nomes_usados[titulo_limpo]})"
            else:
                nomes_usados[titulo_limpo] = 1
                titulo_final = titulo_limpo
                
            chats_formatados.append({"chat_id": chat_id, "titulo": titulo_final})
            
        return {"chats": chats_formatados}
    except Exception as e:
        print("Erro ao listar chats:", e)
        return {"chats": []}