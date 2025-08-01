import React, { useState, useRef, useEffect } from 'react';

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

const ChatbotTester: React.FC = () => {
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

  // Sample conversation starters
  const sampleQuestions = [
    "What are your office hours?",
    "How do I book an appointment?",
    "What services do you offer?",
    "Do you accept insurance?",
    "What should I do in a dental emergency?",
    "How often should I visit the dentist?",
    "Do you offer teeth whitening?",
    "What payment methods do you accept?",
    "How do I prepare for my first visit?",
    "What is included in a dental cleaning?"
  ];

  // Initialize chat session
  useEffect(() => {
    initializeChat();
  }, []);

  // Handle pre-filled query from URL parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const queryParam = urlParams.get('query');
    if (queryParam && currentSession) {
      // Wait a bit for the session to be fully initialized
      setTimeout(() => {
        handleSendMessage(queryParam);
      }, 1000);
    }
  }, [currentSession]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const initializeChat = async () => {
    try {
      // Create a new chat session
      const response = await fetch(`${API_BASE_URL}/api/chatbot/chat/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'admin_tester'
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
      setError('Failed to initialize chat session. Using offline mode.');
      
      // Fallback to offline mode
      const welcomeMessage: ChatMessage = {
        id: '1',
        content: "Hello! I'm your AI dental assistant. I'm currently in test mode with simulated responses. How can I assist you today?",
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
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
            user_id: 'admin_tester'
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
        // Fallback to simulated response
        setTimeout(() => {
          setMessages(prev => prev.filter(msg => msg.id !== 'typing'));
          
          const botMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            content: simulateResponse(text),
            sender: 'bot',
            timestamp: new Date()
          };

          setMessages(prev => [...prev, botMessage]);
        }, 1000);
      }

    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to get response. Using simulated response.');
      
      // Remove typing indicator
      setMessages(prev => prev.filter(msg => msg.id !== 'typing'));
      
      // Add simulated response
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: simulateResponse(text),
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Simulate chatbot response (fallback)
  const simulateResponse = (userMessage: string): string => {
    const message = userMessage.toLowerCase();
    
    if (message.includes('hours') || message.includes('open')) {
      return "We are open Monday to Friday from 9:00 AM to 5:30 PM. We are closed on weekends and major holidays.";
    }
    
    if (message.includes('appointment') || message.includes('book') || message.includes('schedule')) {
      return "You can book an appointment through our online booking system on our website, or call us at (555) 123-4567. We'll be happy to find a time that works for you!";
    }
    
    if (message.includes('services') || message.includes('treatment')) {
      return "We offer comprehensive dental services including cleanings, fillings, crowns, root canals, extractions, wisdom tooth removal, teeth whitening, and emergency dental care. What specific service are you interested in?";
    }
    
    if (message.includes('insurance') || message.includes('payment')) {
      return "Yes, we accept most major dental insurance plans. We also accept cash, credit cards, and offer payment plans for larger procedures. Please contact us to verify if your specific plan is accepted.";
    }
    
    if (message.includes('emergency') || message.includes('urgent') || message.includes('pain')) {
      return "For dental emergencies, please call our office immediately at (555) 123-4567. We provide same-day emergency appointments when possible. If you're experiencing severe pain, don't wait!";
    }
    
    if (message.includes('hello') || message.includes('hi') || message.includes('hey')) {
      return "Hello! How can I help you today? I can answer questions about our services, help you book appointments, or provide information about dental care.";
    }
    
    if (message.includes('thank') || message.includes('thanks')) {
      return "You're welcome! Is there anything else I can help you with today?";
    }
    
    return "I understand you're asking about dental care. While I try to be helpful, I'd recommend calling our office at (555) 123-4567 for specific questions about your dental needs. Our staff can provide personalized assistance!";
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    initializeChat();
  };

  const showMessageSources = (sources: ChatMessage['sources']) => {
    setSelectedMessageSources(sources || []);
    setShowSources(true);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getConfidenceColor = (score?: number) => {
    if (!score) return 'text-gray-400';
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceText = (score?: number) => {
    if (!score) return 'No confidence score';
    if (score >= 0.8) return 'High confidence';
    if (score >= 0.6) return 'Medium confidence';
    return 'Low confidence';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            🤖 Chatbot Tester
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Test your AI dental assistant chatbot with real backend integration
          </p>
        </div>
        <div className="mt-4 flex space-x-2 md:ml-4 md:mt-0">
          <button
            onClick={clearChat}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            🧹 Clear Chat
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <div className="text-yellow-400">⚠️</div>
            <div className="ml-3">
              <p className="text-sm text-yellow-800">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-yellow-400 hover:text-yellow-600"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sample Questions */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Sample Questions</h3>
            <div className="space-y-2">
              {sampleQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleSendMessage(question)}
                  className="w-full text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
                  disabled={isLoading}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>

          {/* Chat Stats */}
          <div className="bg-white rounded-lg shadow p-4 mt-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Chat Stats</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Session:</span>
                <span className="text-sm font-medium">
                  {currentSession ? '🟢 Active' : '🔴 Offline'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Messages:</span>
                <span className="text-sm font-medium">{messages.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">User:</span>
                <span className="text-sm font-medium">
                  {messages.filter(m => m.sender === 'user').length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Bot:</span>
                <span className="text-sm font-medium">
                  {messages.filter(m => m.sender === 'bot').length}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow flex flex-col h-[800px]">
            {/* Chat Header */}
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 font-bold">🤖</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">AI Dental Assistant</p>
                    <p className="text-xs text-gray-500">
                      {isLoading ? 'Typing...' : (currentSession ? 'Connected' : 'Offline Mode')}
                    </p>
                  </div>
                </div>
                {currentSession && (
                  <div className="text-xs text-gray-500">
                    Session: {currentSession.session_id.slice(0, 8)}...
                  </div>
                )}
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.sender === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    {message.isTyping ? (
                      <div className="flex items-center space-x-1">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                        <span className="text-sm">Thinking...</span>
                      </div>
                    ) : (
                      <>
                        <p className="text-sm">{message.content}</p>
                        <div className="flex items-center justify-between mt-1">
                          <p className={`text-xs ${
                            message.sender === 'user' ? 'text-primary-200' : 'text-gray-500'
                          }`}>
                            {formatTime(message.timestamp)}
                          </p>
                          {message.sender === 'bot' && (
                            <div className="flex items-center space-x-2">
                              {message.confidence_score && (
                                <span className={`text-xs ${getConfidenceColor(message.confidence_score)}`}>
                                  {getConfidenceText(message.confidence_score)}
                                </span>
                              )}
                              {message.sources && message.sources.length > 0 && (
                                <button
                                  onClick={() => showMessageSources(message.sources)}
                                  className="text-xs text-blue-600 hover:text-blue-800"
                                >
                                  📚 Sources ({message.sources.length})
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="px-4 py-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  disabled={isLoading}
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={isLoading || !inputMessage.trim()}
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? '⏳' : '📤'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sources Modal */}
      {showSources && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Response Sources</h3>
              <button
                onClick={() => setShowSources(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              {selectedMessageSources?.map((source, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {source.category}
                      </span>
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                        {source.source}
                      </span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Similarity: {(source.similarity_score * 100).toFixed(1)}%
                    </div>
                  </div>
                  <h4 className="font-medium text-gray-900 mb-1">{source.question}</h4>
                  <p className="text-sm text-gray-600">KB ID: {source.kb_id}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default ChatbotTester;