import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  isTyping?: boolean;
  sources?: Array<{
    kb_id: number;
    question: string;
    category: string;
    source: string;
    similarity_score: number;
  }>;
  confidence_score?: number;
}

interface ChatSession {
  session_id: string;
  user_id: string;
  started_at: string;
  is_active: boolean;
}

const Chat: React.FC = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [showSources, setShowSources] = useState(false);
  const [selectedMessageSources, setSelectedMessageSources] = useState<ChatMessage['sources']>([]);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';


  // Initialize chat session
  useEffect(() => {
    initializeChat();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const initializeChat = async () => {
    try {
      // Create a new chat session
      const response = await fetch(`${API_BASE_URL}/api/chatbot/chat/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: `patient_${Date.now()}`
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create chat session');
      }

      const session = await response.json();
      setCurrentSession(session);

      // Add welcome message
      const welcomeMessage: ChatMessage = {
        id: '1',
        content: "Hello! I'm your AI dental assistant. I'm here to help answer questions about our dental services, appointments, and general dental care. How can I assist you today?",
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
      setError(null);

    } catch (err) {
      console.error('Error initializing chat:', err);
      setError('Unable to connect to chat service. Please try refreshing the page.');
      
      // Fallback welcome message
      const fallbackMessage: ChatMessage = {
        id: '1',
        content: "Hello! I'm your AI dental assistant. I'm currently having connection issues, but I'll still try to help you with basic questions about dental care.",
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages([fallbackMessage]);
    }
  };

  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || inputMessage.trim();
    if (!text) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: text,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    // Add typing indicator
    const typingMessage: ChatMessage = {
      id: 'typing',
      content: 'Thinking...',
      sender: 'bot',
      timestamp: new Date(),
      isTyping: true
    };
    setMessages(prev => [...prev, typingMessage]);

    try {
      if (currentSession) {
        // Use real API
        const response = await fetch(`${API_BASE_URL}/api/chatbot/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: text,
            session_id: currentSession.session_id,
            user_id: currentSession.user_id
          })
        });

        if (!response.ok) {
          throw new Error('Failed to get chatbot response');
        }

        const data = await response.json();
        
        // Remove typing indicator
        setMessages(prev => prev.filter(msg => msg.id !== 'typing'));

        // Add bot response
        const botMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          content: data.response,
          sender: 'bot',
          timestamp: new Date(),
          sources: data.sources || [],
          confidence_score: data.confidence_score
        };

        setMessages(prev => [...prev, botMessage]);

      } else {
        // Fallback response
        setTimeout(() => {
          setMessages(prev => prev.filter(msg => msg.id !== 'typing'));
          
          const botMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            content: "I'm sorry, I'm having trouble connecting to our chat service right now. For immediate assistance, please call our office at (555) 123-4567 or use our online appointment booking system.",
            sender: 'bot',
            timestamp: new Date()
          };

          setMessages(prev => [...prev, botMessage]);
        }, 1000);
      }

    } catch (err) {
      console.error('Error sending message:', err);
      setError('Unable to send message. Please check your connection.');
      
      // Remove typing indicator
      setMessages(prev => prev.filter(msg => msg.id !== 'typing'));
      
      // Add error response
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "I apologize, but I'm having trouble responding right now. For immediate assistance, please call our office at (555) 123-4567. Our team will be happy to help you!",
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };


  const showMessageSources = (sources: ChatMessage['sources']) => {
    setSelectedMessageSources(sources || []);
    setShowSources(true);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const startNewChat = () => {
    setMessages([]);
    setCurrentSession(null);
    setError(null);
    initializeChat();
  };

  return (
    <div className="min-h-screen" style={{background: 'linear-gradient(to bottom right, #f9fbff, #a3c9f9)'}}>
      {/* Navigation Header */}
      <nav className="relative z-20 px-4 sm:px-6 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-gray-900 font-semibold text-xl">SmileCare</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <a
              href="/appointments"
              className="px-4 py-2 bg-blue-50/80 hover:bg-blue-100/80 border border-blue-200 text-blue-700 rounded-lg transition-all duration-200 text-sm font-medium backdrop-blur-sm"
              title="Book Appointment"
            >
              📅 Book
            </a>
            <a
              href="/cancel-appointment"
              className="px-4 py-2 bg-blue-50/80 hover:bg-blue-100/80 border border-blue-200 text-blue-700 rounded-lg transition-all duration-200 text-sm font-medium backdrop-blur-sm"
              title="Cancel Appointment"
            >
              ✕ Cancel
            </a>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-blue-50/80 hover:bg-blue-100/80 border border-blue-200 text-blue-700 rounded-lg transition-all duration-200 text-sm font-medium backdrop-blur-sm"
              title="Back to Home"
            >
              ← Home
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative z-10 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Error Alert */}
          {error && (
            <div className="mb-6 bg-red-50/80 backdrop-blur-sm border border-red-200 rounded-xl p-4">
              <div className="flex items-center">
                <div className="text-red-500">⚠️</div>
                <div className="ml-3 flex-1">
                  <p className="text-sm text-red-800 font-medium">{error}</p>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="ml-auto text-red-400 hover:text-red-600"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          {/* Chat Interface */}
          <div className="bg-blue-50/60 backdrop-blur-sm rounded-2xl border border-blue-200 flex flex-col" style={{ height: '75vh' }}>
            {/* Chat Header */}
            <div className="px-6 py-4 border-b border-blue-200 bg-blue-50/80 backdrop-blur-sm rounded-t-2xl">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                  <span className="text-white text-lg">🤖</span>
                </div>
                <div>
                  <p className="text-lg font-medium text-gray-900">AI Dental Assistant</p>
                  <p className="text-sm text-gray-600">
                    {isLoading ? 'Typing...' : (currentSession ? 'Ready to help with your dental questions' : 'Connecting...')}
                  </p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-white/30 backdrop-blur-sm">
                {/* Quick Questions - Show only when no user messages yet */}
                {messages.length <= 1 && (
                  <div className="mb-6">
                    <div className="bg-blue-50/80 backdrop-blur-sm border border-blue-200 rounded-xl p-4">
                      <p className="text-sm text-gray-700 mb-3 text-center font-medium">Try asking:</p>
                      <div className="grid grid-cols-1 gap-2">
                        {[
                          "What are your office hours?",
                          "How do I book an appointment?", 
                          "What services do you offer?"
                        ].map((question, index) => (
                          <button
                            key={index}
                            onClick={() => handleSendMessage(question)}
                            className="w-full text-left p-3 text-sm text-gray-700 bg-white/80 hover:bg-blue-100/80 hover:text-blue-800 rounded-lg border border-blue-200 hover:border-blue-300 transition-all duration-200 backdrop-blur-sm"
                            disabled={isLoading}
                          >
                            {question}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className="flex items-end space-x-2 max-w-xs sm:max-w-sm">
                      {message.sender === 'bot' && (
                        <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center shadow-md">
                          <span className="text-white text-xs">🤖</span>
                        </div>
                      )}
                      
                      <div
                        className={`px-4 py-3 rounded-2xl text-sm ${
                          message.sender === 'user'
                            ? 'bg-blue-600 text-white rounded-br-md shadow-sm'
                            : 'bg-white/90 text-gray-900 border border-blue-200 rounded-bl-md shadow-sm backdrop-blur-sm'
                        }`}
                      >
                        {message.isTyping ? (
                          <div className="flex items-center space-x-2">
                            <div className="flex space-x-1">
                              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            </div>
                            <span className="text-sm text-blue-600 font-medium">Thinking...</span>
                          </div>
                        ) : (
                          <>
                            <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                            <div className="flex items-center justify-between mt-2">
                              <p className={`text-xs ${
                                message.sender === 'user' ? 'text-blue-200' : 'text-gray-400'
                              }`}>
                                {formatTime(message.timestamp)}
                              </p>
                              {message.sender === 'bot' && message.sources && message.sources.length > 0 && (
                                <button
                                  onClick={() => showMessageSources(message.sources)}
                                  className="text-xs text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2 py-1 rounded-full transition-colors duration-200 font-medium"
                                >
                                  📚 {message.sources.length}
                                </button>
                              )}
                            </div>
                          </>
                        )}
                      </div>
                      
                      {message.sender === 'user' && (
                        <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-gray-400 to-gray-500 rounded-full flex items-center justify-center shadow-md">
                          <span className="text-white text-xs">👤</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

            {/* Input Area */}
            <div className="border-t border-gray-100 p-3 bg-gray-50 rounded-b-xl">
              <div className="flex space-x-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  placeholder="Ask about dental services, appointments..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm text-sm"
                  disabled={isLoading}
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={isLoading || !inputMessage.trim()}
                  className="px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-full hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-md hover:shadow-lg"
                >
                  {isLoading ? '⏳' : '📤'}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2 text-center px-2">
                💡 For personalized medical advice, please consult our dental professionals.
              </p>
            </div>
          </div>
        </div>



      </div>

      {/* Sources Modal - Mobile Optimized */}
      {showSources && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
          <div className="bg-white rounded-xl w-full max-w-lg p-4 max-h-[80vh] overflow-y-auto shadow-2xl border border-blue-100">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-sm">📚</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900">Sources</h3>
              </div>
              <button
                onClick={() => setShowSources(false)}
                className="text-gray-400 hover:text-gray-600 text-xl p-1 hover:bg-gray-100 rounded-full"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-3">
              {selectedMessageSources?.map((source, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gradient-to-r from-gray-50 to-blue-50">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-500 text-white">
                      {source.category}
                    </span>
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-500 text-white">
                      {(source.similarity_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2 text-sm">{source.question}</h4>
                  <p className="text-xs text-gray-600 bg-white px-2 py-1 rounded border">
                    <span className="font-medium">Source:</span> {source.source}
                  </p>
                </div>
              ))}
            </div>
            
            <div className="mt-4 text-center">
              <button
                onClick={() => setShowSources(false)}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 font-medium shadow-md hover:shadow-lg text-sm"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;