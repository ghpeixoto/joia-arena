# ✺ JoIA — Arena de Inteligência Artificial

> Plataforma de chat que coloca modelos de IA para competir entre si, gerando respostas otimizadas através de rodadas de debate e auditoria automática.

---

## 💡 Como funciona

O usuário envia uma mensagem. Em vez de apenas chamar um único modelo, o JoIA lança o pedido simultaneamente para **GPT-4o** e **Gemini 2.5 Flash**, e então os coloca para se auditar mutuamente em um loop competitivo:

1. **Rodada inicial** — Ambos os modelos geram uma resposta independente
2. **Auditoria cruzada** — Cada modelo analisa o código/resposta do outro, identificando falhas e propondo uma versão melhorada
3. **Loop de batalha** — O processo se repete até que ambos atinjam **98%+ de certeza técnica** (máx. 12 rodadas)
4. **Resultado final** — O frontend exibe as duas versões rankeadas, com explicação detalhada da evolução

---

## 🏗️ Arquitetura

```
joia-arena/
├── backend/
│   ├── main.py          # API FastAPI com streaming SSE
│   └── moreprod_db.sqlite  # Banco local (histórico de chats)
└── frontend/
    ├── app/
    │   ├── page.tsx     # Interface principal do chat
    │   └── layout.tsx   # Layout global
    └── components/
        └── TypingEffect.tsx  # Animação de digitação
```

**Fluxo de dados:**
```
Usuário → Next.js → FastAPI → GPT-4o ──┐
                                        ├── Debate → Resultado Final
                             Gemini 2.5 ┘
```

---

## 🛠️ Tecnologias

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — API assíncrona com streaming SSE
- [OpenAI API](https://platform.openai.com/) — GPT-4o
- [Google Gemini API](https://ai.google.dev/) — Gemini 2.5 Flash
- SQLite — Persistência de histórico de conversas
- Python `asyncio` — Chamadas paralelas aos modelos

**Frontend**
- [Next.js 16](https://nextjs.org/) — Framework React
- [Tailwind CSS 4](https://tailwindcss.com/) — Estilização
- [Lucide React](https://lucide.dev/) — Ícones
- TypeScript — Tipagem estática

---

## 🚀 Como rodar localmente

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure suas chaves em backend/.env
OPENAI_API_KEY=...
GEMINI_API_KEY=...

python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Acesse **http://localhost:3000**

---

## ✨ Destaques técnicos

- **Streaming em tempo real** via Server-Sent Events (SSE) — o placar de certeza atualiza ao vivo enquanto os modelos debatem
- **Memória de contexto** — o histórico da conversa é carregado a cada nova mensagem
- **Sistema anti-duplicação** de títulos na sidebar
- **Sabedoria diária** — respostas de alta certeza são reutilizadas como contexto em novas conversas
