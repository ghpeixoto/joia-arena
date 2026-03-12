'use client';

import { useState, useRef, useEffect } from 'react';
import { Search, MessageSquare, Plus, ArrowUp, X, Swords } from 'lucide-react';
import { TypingEffect } from '@/components/TypingEffect';

const ACCENT_COLOR = '#D946EF'; 

const getGreetingByTimezone = () => {
  const now = new Date().toLocaleTimeString('en-US', { timeZone: 'America/Sao_Paulo', hour12: false });
  const hour = parseInt(now.split(':')[0], 10);
  if (hour >= 5 && hour < 12) return 'Bom dia';
  if (hour >= 12 && hour < 18) return 'Boa tarde';
  return 'Boa noite';
};

export default function Home() {
  const [step, setStep] = useState('intro');
  const [name, setName] = useState('');
  const [greeting, setGreeting] = useState('Olá');
  
  const [showIntroBtn, setShowIntroBtn] = useState(false);
  const [showNameInput, setShowNameInput] = useState(false);
  
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<{id: number, role: string, content: string, image?: string}[]>([]);
  const [attachedImage, setAttachedImage] = useState<string | null>(null);
  const [zoomedImage, setZoomedImage] = useState<string | null>(null);
  
  const [isProcessing, setIsProcessing] = useState(false); 
  const [arenaStatus, setArenaStatus] = useState({ active: false, rodada: 0, gpt: 0, gemini: 0 });
  
  const [sidebarChats, setSidebarChats] = useState<{chat_id: string, titulo: string}[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string>("");
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const savedName = localStorage.getItem('joia_name');
    if (savedName) {
      setName(savedName);
      setStep('chat'); 
    } else {
      const timerBtn = setTimeout(() => setShowIntroBtn(true), 3500);
      return () => clearTimeout(timerBtn);
    }
  }, []);

  useEffect(() => {
    if (step === 'nome') {
      const timer = setTimeout(() => setShowNameInput(true), 2000);
      return () => clearTimeout(timer);
    }
  }, [step]);

  const fetchSidebar = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/chats');
      const data = await res.json();
      setSidebarChats(data.chats);
      return data.chats;
    } catch (e) { console.error(e); return []; }
  };

  useEffect(() => {
    if (step === 'chat') {
      setGreeting(getGreetingByTimezone());
      fetchSidebar().then(chats => {
        if (!currentChatId) {
          setCurrentChatId(chats.length > 0 ? chats[0].chat_id : crypto.randomUUID());
        }
      });
    }
  }, [step]);

  useEffect(() => {
    if (!currentChatId) return;
    const fetchHistory = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/historico/${currentChatId}`);
        const data = await res.json();
        if (data.messages && data.messages.length > 0) {
          setMessages(data.messages.map((m: any, i: number) => ({
            id: Date.now() + i, role: m.role, content: m.content,
            image: m.image_b64 ? `data:image/jpeg;base64,${m.image_b64}` : undefined
          })));
        } else {
          setMessages([]); 
        }
      } catch (e) { console.error(e); }
    };
    fetchHistory();
  }, [currentChatId]);

  const handleNameSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && name.trim() !== '') {
      localStorage.setItem('joia_name', name.trim());
      setStep('chat');
    }
  };

  const handleNameButtonClick = () => {
    if (name.trim()) {
      localStorage.setItem('joia_name', name.trim());
      setStep('chat');
    }
  }

  const handleNewChat = () => {
    setCurrentChatId(crypto.randomUUID());
    setMessages([]);
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setAttachedImage(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleSendMessage = async () => {
    if ((!inputText.trim() && !attachedImage) || isProcessing) return;

    const userMessage = inputText;
    const userImage = attachedImage;
    
    // --- CORREÇÃO DE SEGURANÇA: Garante que o chat_id nunca vai vazio ---
    const activeChatId = currentChatId || crypto.randomUUID();
    if (!currentChatId) setCurrentChatId(activeChatId);

    setMessages(prev => [...prev, { id: Date.now(), role: 'user', content: userMessage, image: userImage || undefined }]);
    setInputText('');
    setAttachedImage(null);
    setIsProcessing(true);
    setArenaStatus({ active: true, rodada: 0, gpt: 0, gemini: 0 });

    try {
      const base64Clean = userImage ? userImage.split(',')[1] : null;

      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: activeChatId, mensagem: userMessage, imagem_b64: base64Clean })
      });

      if (!response.body) throw new Error("Sem resposta do servidor.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let finalMessage = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || ""; 

        for (const part of parts) {
          if (part.startsWith('data: ')) {
            const dataObj = JSON.parse(part.substring(6));
            if (dataObj.type === 'progress') {
              setArenaStatus({ active: true, rodada: dataObj.rodada, gpt: dataObj.gpt, gemini: dataObj.gemini });
            } else if (dataObj.type === 'final') {
              finalMessage = dataObj.resposta;
            }
          }
        }
      }

      setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', content: finalMessage }]);
      fetchSidebar(); // Atualiza a barra lateral no final

    } catch (error) {
      setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', content: 'Erro de comunicação.' }]);
    } finally {
      setIsProcessing(false);
      setArenaStatus({ active: false, rodada: 0, gpt: 0, gemini: 0 });
    }
  };

  const JoiaLogo = ({ size = 40, className = "" }: { size?: number, className?: string }) => (
    <div style={{ fontSize: `${size}px`, lineHeight: 1, textShadow: `0 0 ${size/2}px ${ACCENT_COLOR}66` }} className={`mb-4 grayscale-0 ${className}`}>⚔️</div>
  );

  return (
    <main className="min-h-screen flex bg-[#2b2a27] text-[#E4DECE]">
      
      {step === 'intro' && (
        <div className="max-w-[650px] mx-auto mt-[15vh] w-full p-6 flex flex-col">
          <JoiaLogo size={60} />
          <h1 className="text-[36px] font-serif mb-4 leading-tight min-h-[45px]"><TypingEffect text="Olá! Eu sou o JoIA," speed={40} /></h1>
          <p className={`text-[22px] text-[${ACCENT_COLOR}] leading-relaxed min-h-[80px]`}><TypingEffect text="uma arena de IA pensada para você produzir mais, com agilidade e eficiência." speed={30} /></p>
          <div className={`mt-8 transition-opacity duration-1000 ease-in-out ${showIntroBtn ? 'opacity-100' : 'opacity-0'}`}>
            <button onClick={() => setStep('nome')} disabled={!showIntroBtn} className="px-8 bg-[#E4DECE] text-[#2b2a27] font-medium py-3 rounded-xl hover:bg-white transition-colors text-[17px]">Vamos começar</button>
          </div>
        </div>
      )}

      {step === 'nome' && (
        <div className="max-w-[550px] mx-auto mt-[20vh] w-full flex flex-col items-center p-6">
          <JoiaLogo size={60} />
          <h1 className="text-[32px] font-serif text-center min-h-[50px] mb-6"><TypingEffect text="Antes de começarmos, como devo chamá-lo?" speed={35} /></h1>
          <div className={`w-full relative transition-all duration-1000 ease-in-out ${showNameInput ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
            <input type="text" placeholder="Digite seu nome" value={name} onChange={(e) => setName(e.target.value)} onKeyDown={handleNameSubmit} autoFocus={showNameInput} className={`w-full bg-transparent border border-[#555] rounded-2xl p-4 pl-5 text-[#E4DECE] text-[16px] focus:outline-none focus:border-[${ACCENT_COLOR}] transition-colors`} />
            <button onClick={handleNameButtonClick} className={`absolute right-3 top-3 p-1.5 rounded-lg transition-colors ${name.trim() ? 'bg-[#E4DECE] text-[#2b2a27]' : 'bg-[#42413e] text-[#888]'}`}><ArrowUp size={20} /></button>
          </div>
        </div>
      )}

      {step === 'chat' && (
        <div className="flex w-full h-screen">
          
          <div className="w-[260px] bg-[#22211f] border-r border-[#383734] flex flex-col pt-4 pb-4">
            <div className="px-4 mb-6 flex items-center gap-3"><JoiaLogo size={28} className="!mb-0" /><h2 className="text-[20px] font-serif font-medium text-[#E4DECE] tracking-wide">JoIA</h2><Swords size={18} className={`text-[${ACCENT_COLOR}] ml-auto opacity-80`} /></div>
            
            <div className="px-3 space-y-1">
              <button onClick={handleNewChat} className="w-full flex items-center gap-3 text-[#E4DECE] hover:bg-[#33322f] p-2 rounded-lg text-[14px] font-medium transition-colors"><Plus size={18} /> Novo bate-papo</button>
              <button className="w-full flex items-center gap-3 text-[#E4DECE] hover:bg-[#33322f] p-2 rounded-lg text-[14px] font-medium transition-colors"><Search size={18} /> Procurar</button>
            </div>
            
            <div className="mt-8 px-4 text-[11px] text-[#888] font-bold tracking-wider uppercase mb-2">Recentes</div>
            <div className="flex-1 overflow-y-auto px-2 space-y-0.5 scrollbar-thin scrollbar-thumb-[#42413e]">
              {sidebarChats.length === 0 ? (
                <p className="text-[13px] text-[#666] p-2 ml-1">Nenhum chat salvo</p>
              ) : (
                sidebarChats.map(chat => (
                  <button 
                    key={chat.chat_id}
                    onClick={() => setCurrentChatId(chat.chat_id)}
                    className={`w-full flex items-center gap-2 text-left truncate p-2 rounded-lg text-[13px] transition-colors ${currentChatId === chat.chat_id ? 'bg-[#33322f] text-[#E4DECE]' : 'text-[#A3A3A3] hover:bg-[#33322f] hover:text-[#E4DECE]'}`}
                  >
                    <MessageSquare size={14} className="shrink-0 opacity-70" />
                    <span className="truncate">{chat.titulo}</span>
                  </button>
                ))
              )}
            </div>
            
            <div className="mt-auto px-3 pt-4 border-t border-[#383734]">
              <button className="w-full flex items-center gap-3 hover:bg-[#33322f] p-2 rounded-lg transition-colors group">
                <div className={`w-8 h-8 rounded-full bg-[${ACCENT_COLOR}] text-[#fff] flex items-center justify-center font-bold text-[14px] group-hover:brightness-110 transition-all`}>{name.charAt(0).toUpperCase()}</div>
                <div className="text-left leading-tight"><div className="text-[14px] font-medium text-[#E4DECE]">{name}</div><div className="text-[11px] text-[#A3A3A3]">Arena JoIA</div></div>
              </button>
            </div>
          </div>

          <div className="flex-1 flex flex-col relative bg-[#2b2a27]">
            <div className="flex-1 overflow-y-auto p-6 md:px-20 scrollbar-thin scrollbar-thumb-[#42413e] scrollbar-track-transparent pb-32">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full -mt-20">
                  <div className="flex flex-col items-center gap-6 mb-8 animate-[fadeIn_0.5s_ease-out]">
                    <JoiaLogo size={80} />
                    <h1 className="text-[42px] font-serif text-[#E4DECE]">{greeting}, <span className={`text-[${ACCENT_COLOR}] drop-shadow-sm`}>{name}</span></h1>
                  </div>
                </div>
              ) : (
                <div className="max-w-[800px] mx-auto w-full space-y-8 mt-10">
                  {messages.map(msg => (
                    <div key={msg.id} className="flex flex-col animate-[fadeIn_0.3s_ease-in]">
                      <div className="flex items-center gap-3 mb-2">
                        {msg.role === 'user' ? (
                          <div className={`w-8 h-8 rounded-full bg-[${ACCENT_COLOR}] text-white flex items-center justify-center font-bold text-[13px] shrink-0`}>{name.charAt(0).toUpperCase()}</div>
                        ) : (
                          <div className={`shrink-0 rounded-full overflow-hidden w-8 h-8 border border-[${ACCENT_COLOR}]/40 flex items-center justify-center pt-1 bg-[${ACCENT_COLOR}]/10`}><JoiaLogo size={20} className="!mb-0" /></div>
                        )}
                        <span className="font-semibold text-[15px] text-[#E4DECE]">{msg.role === 'user' ? name : 'JoIA'}</span>
                      </div>
                      <div className="pl-11 text-[16px] leading-relaxed text-[#E4DECE]/90 space-y-4 font-light">
                        {msg.image && <img src={msg.image} alt="Anexo" className="max-w-[300px] rounded-xl border border-[#42413e]/50 cursor-zoom-in hover:opacity-90 transition-opacity shadow-lg" onClick={() => setZoomedImage(msg.image || null)} />}
                        {msg.content && <div className="prose prose-invert max-w-none"><pre className="whitespace-pre-wrap font-sans">{msg.content}</pre></div>}
                      </div>
                    </div>
                  ))}
                  
                  {arenaStatus.active && (
                    <div className="flex flex-col animate-[fadeIn_0.3s_ease-in] max-w-[600px] mt-4 ml-11">
                      <div className="bg-[#302f2c] border border-[#42413e] rounded-2xl p-5 shadow-lg relative overflow-hidden">
                        <div className="text-center text-[#E4DECE] font-serif mb-5 flex items-center justify-center gap-2">
                          <Swords size={20} className={`text-[${ACCENT_COLOR}] animate-pulse`} /> 
                          <span>Arena JoIA em Andamento (Rodada {arenaStatus.rodada}/12)</span>
                          <Swords size={20} className={`text-[${ACCENT_COLOR}] animate-pulse`} />
                        </div>
                        <div className="space-y-5">
                          <div>
                            <div className="flex justify-between text-xs mb-1.5 font-medium text-[#A3A3A3]"><span>🔵 GPT-4o</span><span>{arenaStatus.gpt}%</span></div>
                            <div className="w-full bg-[#22211f] rounded-full h-3 overflow-hidden border border-[#42413e]">
                              <div className="bg-[#2563EB] h-3 rounded-full transition-all duration-500 ease-out relative" style={{ width: `${arenaStatus.gpt}%` }}><div className="absolute right-1 top-0 text-[10px] drop-shadow-md">⚔️</div></div>
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between text-xs mb-1.5 font-medium text-[#A3A3A3]"><span>🔴 Gemini 2.5</span><span>{arenaStatus.gemini}%</span></div>
                            <div className="w-full bg-[#22211f] rounded-full h-3 overflow-hidden border border-[#42413e]">
                              <div className={`bg-[${ACCENT_COLOR}] h-3 rounded-full transition-all duration-500 ease-out relative`} style={{ width: `${arenaStatus.gemini}%` }}><div className="absolute right-1 top-0 text-[10px] drop-shadow-md">⚔️</div></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="p-4 max-w-[850px] mx-auto w-full shrink-0">
              <div className={`bg-[#302f2c] border border-[#42413e] rounded-[24px] flex flex-col p-3 shadow-2xl relative focus-within:border-[${ACCENT_COLOR}]/50 transition-colors`}>
                {attachedImage && (
                  <div className="mb-3 relative inline-block ml-2 mt-2">
                    <img src={attachedImage} alt="Preview" className="h-20 w-20 object-cover rounded-xl border border-[#555] shadow-md" />
                    <button onClick={() => setAttachedImage(null)} className={`absolute -top-2 -right-2 bg-[#2b2a27] border border-[#42413e] text-[#ececec] rounded-full p-1 hover:bg-[${ACCENT_COLOR}] transition-colors`}><X size={14} /></button>
                  </div>
                )}
                <textarea rows={1} placeholder="Como a JoIA pode te ajudar a produzir mais hoje?" value={inputText} onChange={(e) => setInputText(e.target.value)} onKeyDown={(e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); } }} disabled={isProcessing} className="w-full bg-transparent text-[#E4DECE] p-3 pl-4 text-[16px] focus:outline-none placeholder-[#888] resize-none overflow-hidden min-h-[50px] disabled:opacity-50" style={{ height: inputText ? `${Math.min(inputText.split('\n').length * 24 + 24, 200)}px` : '50px' }} />
                <div className="flex justify-between items-center mt-2 px-2">
                  <input type="file" ref={fileInputRef} className="hidden" accept="image/*" onChange={handleImageUpload} />
                  <button onClick={() => fileInputRef.current?.click()} disabled={isProcessing} className={`text-[#888] hover:text-[${ACCENT_COLOR}] transition-colors p-2 rounded-full hover:bg-[#42413e]/50 disabled:opacity-50`}><Plus size={22} /></button>
                  <button onClick={handleSendMessage} disabled={(!inputText.trim() && !attachedImage) || isProcessing} className={`p-2 rounded-xl transition-all duration-200 ${((inputText.trim() || attachedImage) && !isProcessing) ? `bg-[${ACCENT_COLOR}] text-white hover:brightness-110 shadow-md transform hover:scale-105` : 'bg-[#42413e] text-[#888] cursor-not-allowed'}`}><ArrowUp size={20} strokeWidth={2.5} className={isProcessing ? "animate-bounce" : ""} /></button>
                </div>
              </div>
              <div className="text-center mt-3 text-[11px] text-[#666] font-medium tracking-wide uppercase">Arena JoIA - Potencializada por Múltiplas IAs</div>
            </div>
          </div>
        </div>
      )}
      {zoomedImage && (<div className="fixed inset-0 z-50 bg-[#1e1e1e]/95 flex items-center justify-center p-8 cursor-zoom-out backdrop-blur-md animate-[fadeIn_0.2s_ease-out]" onClick={() => setZoomedImage(null)}><img src={zoomedImage} alt="Zoom" className="max-w-full max-h-full object-contain rounded-lg shadow-[0_0_50px_rgba(0,0,0,0.5)] scale-100 animate-[scaleIn_0.3s_ease-out]" /></div>)}
    </main>
  );
}