import { marked } from 'marked';
import DOMPurify from 'dompurify';
import React, { useState, useEffect, useRef } from 'react';

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export default function Chat({ analysisContext }) {
  const [messages, setMessages] = useState([{ role: "assistant", content: "Hi! I am ASTra, your AI assistant. Analyze some code, and ask me to explain or optimize it further!" }]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    
    const userMsg = input.trim();
    setInput("");
    
    const history = messages.slice(1);
    
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setIsTyping(true);

    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMsg,
          history: history,
          analysis_context: analysisContext
        })
      });

      if (!res.ok) throw new Error("Server error");

      setMessages(prev => [...prev, { role: "assistant", content: "" }]);
      
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunkText = decoder.decode(value, { stream: true });
        const lines = chunkText.split("\n");
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const dataStr = line.slice(6).trim();
          if (dataStr === "[DONE]") continue;

          try {
            const data = JSON.parse(dataStr);
            if (data.content) {
              assistantContent += data.content;
              setMessages(prev => {
                const newMsgs = [...prev];
                newMsgs[newMsgs.length - 1].content = assistantContent;
                return newMsgs;
              });
            }
          } catch (e) {}
        }
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: "assistant", content: "❌ Error connecting to chat server." }]);
    } finally {
      setIsTyping(false);
      scrollToBottom();
    }
  };

  return (
    <div className="chat-widget-container">
      {isOpen && (
        <div className="glass-panel chat-window">
          <div className="board-header">ASTra Chat</div>
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.role === 'user' ? 'msg-user' : 'msg-assistant'}`}>
                <div className="markdown-body" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(msg.content)) }} />
              </div>
            ))}
            {isTyping && (
              <div className="message msg-assistant">
                <span style={{fontStyle: 'italic', color: 'var(--text-muted)'}}>ASTra is typing...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className="chat-input-area">
            <input 
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about the analysis or code..."
            />
            <button className="send-btn" onClick={handleSend} disabled={isTyping || !input.trim()}>
              ➤
            </button>
          </div>
        </div>
      )}
      <button className="chat-toggle-btn" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? '✕' : '💬'}
      </button>
    </div>
  );
}
