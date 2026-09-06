"use client";
import { Upload, Send, FileText, Bot, User, Loader2, CheckCircle2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { PatraLogo } from "./logo"; // Adjust path if you put it in a components folder
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
const API_BASE_URL = process.env.SERVER_PUBLIC_API_URL || "http://localhost:8000";
type Message = {
  role: "user" | "ai";
  content: string;
};

export default function RAGDashboard() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "ai", content: "Hello! I am ready to answer questions based on your documents. Please upload a PDF to get started." }
  ]);
  const [input, setInput] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

 const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadStatus(null);
    const formData = new FormData();

    // Append all selected files to the FormData object
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }

    try {
      const res = await fetch(`${API_BASE_URL}/upload`, {
      method: "POST",
      body: formData,
    });
      const data = await res.json();
      
      if (res.ok) {
        setUploadStatus(`Success: ${data.processed.length} file(s) added.`);
      } else {
        setUploadStatus(`Error: ${data.detail}`);
      }
    } catch (error) {
      setUploadStatus("Failed to connect to the server.");
    } finally {
      setIsUploading(false);
      // Reset the input so the user can upload the same files again if needed
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setIsTyping(true);

    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: userMessage }),
    });
      
      const data = await res.json();
      
      setMessages(prev => [...prev, { 
        role: "ai", 
        content: res.ok ? data.answer : `Error: ${data.detail}` 
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: "ai", content: "Sorry, I couldn't reach the server. Is FastAPI running?" }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 font-sans">
      
      {/* Sidebar / Knowledge Base Panel */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col p-6">
        <h2 className="text-xl font-semibold mb-6 text-gray-800 flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-600"/>
          Knowledge Base
        </h2>
        
<label className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:bg-gray-50 transition-colors cursor-pointer block relative">
          <input 
            type="file" 
            accept=".pdf" 
            multiple /* NEW: This enables selecting multiple files */
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
            onChange={handleFileUpload}
            disabled={isUploading}
            ref={fileInputRef} /* Ensure this is here so we can reset it */
          />
          {isUploading ? (
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-500 mb-2" />
          ) : (
            <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
          )}
          <p className="text-sm text-gray-600 font-medium relative z-10">
            {isUploading ? "Processing Documents..." : "Click to upload PDFs"}
          </p>
        </label>

        {uploadStatus && (
          <div className={`mt-4 p-3 rounded-lg text-sm flex items-start gap-2 ${uploadStatus.includes('Success') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{uploadStatus}</span>
          </div>
        )}
      </div>

      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col bg-white">
        <div className="border-b border-gray-100 p-6 shadow-sm z-10 flex items-center gap-4">
          <PatraLogo className="w-12 h-12" />
          <div>
            <h1 className="text-2xl font-bold bg-linear-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              PatraAI
            </h1>
            <p className="text-sm text-gray-500">Your intelligent document assistant</p>
          </div>
        </div>

        {/* Chat History */}
<div className="flex-1 overflow-y-auto p-6 space-y-6">
  {messages.map((msg, idx) => (
    <div key={idx} className={`flex gap-4 max-w-4xl mx-auto ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
      <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200 text-blue-600 shadow-sm'}`}>
        {msg.role === 'user' ? <User className="w-5 h-5"/> : <Bot className="w-5 h-5"/>}
      </div>
      
      <div className={`p-4 rounded-2xl max-w-[85%] ${
        msg.role === 'user' 
          ? 'bg-blue-600 text-white rounded-tr-none' 
          : 'bg-white border border-gray-100 shadow-sm rounded-tl-none'
      }`}>
        {msg.role === 'user' ? (
          <div className="leading-relaxed">{msg.content}</div>
        ) : (
          <div className="prose prose-sm md:prose-base max-w-none text-gray-700 prose-headings:text-gray-800 prose-headings:font-semibold prose-a:text-blue-600 hover:prose-a:text-blue-500 prose-strong:text-gray-900 prose-p:leading-relaxed prose-ul:list-disc prose-ol:list-decimal">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {msg.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  ))}
          
          {isTyping && (
            <div className="flex gap-4 max-w-4xl mx-auto">
              <div className="w-10 h-10 rounded-full bg-gray-100 text-gray-600 flex items-center justify-center shrink-0">
                <Bot className="w-5 h-5"/>
              </div>
              <div className="p-4 bg-gray-100 rounded-2xl rounded-tl-none flex items-center gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-6 bg-white border-t border-gray-100">
          <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your files..."
              className="w-full pl-6 pr-16 py-4 bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all text-gray-800"
              disabled={isTyping}
            />
            <button 
              type="submit" 
              disabled={!input.trim() || isTyping}
              className="absolute right-2 top-2 bottom-2 aspect-square bg-blue-600 text-white rounded-full flex items-center justify-center hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors"
            >
              <Send className="w-5 h-5 -ml-0.5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}