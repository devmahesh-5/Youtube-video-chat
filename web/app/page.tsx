'use client';
import React, { useState, useEffect, useRef } from 'react';
import { Send, FileText, Database, Search, MessageSquare, Youtube, Link as LinkIcon, Loader2 } from 'lucide-react';

const RAGHomePage = () => {
  const [urlInput, setUrlInput] = useState('');
  const [videoId, setVideoId] = useState<string | null>(null);
  const [isIngesting, setIsIngesting] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [answer, setAnswer] = useState(''); // Current streaming answer
  const [isTyping, setIsTyping] = useState(false);
  
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when answer updates
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [answer]);

  const extractVideoId = (url: string) => {
    const regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[7].length === 11) ? match[7] : null;
  };

  // --- REQUEST 1: INGEST ---
  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const id = extractVideoId(urlInput);
    if (!id) return alert("Please enter a valid YouTube URL");

    setVideoId(id);
    setIsIngesting(true);
    setAnswer('');

    try {
      const response = await fetch('http://localhost:8000/api/retrive', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_id: id }),
      });

      if (!response.ok) throw new Error("Ingestion failed");
      
      const data = await response.json();
    } catch (err) {
      alert("Error processing video.", err);
    } finally {
      setIsIngesting(false);
    }
  };

 
  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput || !videoId || isIngesting) return;

    const query = chatInput;
    setChatInput('');
    setAnswer('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_id: videoId, query }),
      });

      if (!response.body) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        // Process SSE format "data: {...}"
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              setAnswer((prev) => prev + data.token);
            } catch (e) {
              console.error("Error parsing chunk", e);
            }
          }
        }
      }
    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0f0f0f] text-white font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/10 flex flex-col hidden md:flex">
        <div className="p-4 flex items-center gap-2 font-bold text-xl text-red-600">
          <Youtube size={28} fill="currentColor" />
          <span className="text-white">VideoRAG</span>
        </div>
        <nav className="flex-1 px-2 mt-4 space-y-1 text-sm">
            <div className={`p-3 rounded-lg flex items-center gap-3 cursor-pointer ${videoId ? 'bg-white/10' : 'text-gray-500'}`}>
                <MessageSquare size={18} /> <span>{isIngesting ? 'Analyzing...' : 'Active Session'}</span>
            </div>
        </nav>
      </aside>

      <main className="flex-1 flex flex-col min-w-0 bg-black overflow-hidden">
        {/* Header / URL Bar */}
        <header className="h-16 flex items-center justify-center px-6 border-b border-white/10 bg-[#0f0f0f]">
          <form onSubmit={handleUrlSubmit} className="flex-1 max-w-3xl relative group">
            <input 
              type="text" 
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              disabled={isIngesting}
              placeholder="Paste YouTube URL to analyze(make sure transcript is available)..." 
              className="w-full bg-[#121212] border border-white/10 rounded-full py-2 px-12 focus:border-red-600 outline-none transition disabled:opacity-50"
            />
            <LinkIcon className="absolute left-4 top-2.5 text-gray-400" size={18} />
            <button 
              type="submit"
              disabled={isIngesting}
              className="absolute right-2 top-1.5 bg-red-600 hover:bg-red-700 disabled:bg-zinc-700 text-white text-xs font-bold py-1.5 px-4 rounded-full transition"
            >
              {isIngesting ? <Loader2 className="animate-spin" size={16}/> : 'ANALYZE'}
            </button>
          </form>
        </header>

        <div className="flex-1 overflow-y-auto p-6" ref={scrollRef}>
          <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <div className="lg:col-span-2 space-y-6">
              {/* Video Player */}
              <div className="aspect-video w-full bg-zinc-900 rounded-xl overflow-hidden border border-white/10 shadow-2xl relative">
                {isIngesting && (
                    <div className="absolute inset-0 z-10 bg-black/80 flex flex-col items-center justify-center">
                        <Loader2 className="animate-spin text-red-600 mb-2" size={40} />
                        <p className="text-sm font-medium">Extracting Transcript & Embedding Vectors...</p>
                    </div>
                )}
                {videoId ? (
                  <iframe width="100%" height="100%" src={`https://www.youtube.com/embed/${videoId}`} title="YouTube player" frameBorder="0" allowFullScreen />
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-gray-500 p-8 text-center">
                    <Youtube size={48} className="mb-4 opacity-20" />
                    <p>Ready to analyze video content.</p>
                  </div>
                )}
              </div>

              {/* Chat/Response Display */}
              <div className="space-y-4">
                <h1 className="text-xl font-bold flex items-center gap-2">
                    {videoId && <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"/>}
                    {videoId ? "AI Insights" : "Waiting for Video..."}
                </h1>
                <div className="bg-[#121212] border border-white/10 rounded-xl p-6 min-h-[250px] text-gray-200 leading-relaxed whitespace-pre-wrap shadow-inner">
                  {answer ? (
                    answer
                  ) : isTyping ? (
                    <span className="animate-pulse text-gray-500 italic">AI is thinking...</span>
                  ) : (
                    <p className="italic text-gray-500 text-sm">
                        {videoId ? "Video indexed! Ask your first question below." : "Transcript data will appear here."}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Right Sidebar: Sources */}
            <div className="space-y-4">
              <h3 className="font-bold text-sm uppercase text-gray-400 tracking-wider">References</h3>
              <div className="bg-white/5 border border-white/10 rounded-lg p-4 text-xs text-gray-400">
                  Sources found in the vector store will be highlighted here during the chat.
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Chat Bar */}
        <footer className="p-4 bg-[#0f0f0f] border-t border-white/10">
          <form onSubmit={handleChatSubmit} className="max-w-4xl mx-auto flex gap-4 items-center">
            <div className="w-8 h-8 rounded-full bg-red-600 shrink-0 flex items-center justify-center text-xs font-bold">AI</div>
            <input 
              type="text" 
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              disabled={!videoId || isIngesting}
              placeholder={!videoId ? "Paste a link first..." : "Ask about the video..."}
              className="flex-1 bg-[#121212] border border-white/10 rounded-lg py-2 px-4 outline-none focus:border-red-600 transition disabled:opacity-50"
            />
            <button 
                type="submit"
                disabled={!videoId || isIngesting || isTyping}
                className="p-2 hover:bg-white/10 rounded-full transition disabled:opacity-30"
            >
              <Send size={20} className={isTyping ? "text-red-600 animate-bounce" : "text-gray-400"} />
            </button>
          </form>
        </footer>
      </main>
    </div>
  );
};

export default RAGHomePage;