import { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    id: string;
    content: string;
    metadata: any;
    relevance: number;
  }>;
}

interface Category {
  id: string;
  name: string;
}

export function PayrollAssistant() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [taxYears, setTaxYears] = useState<string[]>([]);
  const [showSources, setShowSources] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch categories on mount
  useEffect(() => {
    fetchCategories();
    fetchTaxYears();
    addWelcomeMessage();
  }, []);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addWelcomeMessage = () => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: `Welcome to the Payroll Tax Assistant! I'm here to help you with questions about South African payroll tax, including:

• Income tax brackets and calculations
• Tax rebates (primary, secondary, tertiary)
• Tax thresholds and exemptions
• UIF contributions and caps
• Skills Development Levy (SDL)
• Employment Tax Incentive (ETI)
• Medical scheme tax credits

I have tax data available from 2021 to 2025. How can I help you today?`,
      },
    ]);
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/assistant/categories/');
      const data = await response.json();
      setCategories(
        data.categories.map((cat: string) => ({
          id: cat,
          name: cat.charAt(0).toUpperCase() + cat.slice(1).replace(/_/g, ' '),
        }))
      );
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchTaxYears = async () => {
    try {
      const response = await fetch('/api/assistant/tax-years/');
      const data = await response.json();
      setTaxYears(data.tax_years || []);
    } catch (error) {
      console.error('Failed to fetch tax years:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputValue,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/assistant/query/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: inputValue,
          category: selectedCategory || undefined,
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.answer || 'I apologize, but I could not process your question. Please try again.',
        sources: data.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your question. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSources = (messageId: string) => {
    setShowSources((prev) => ({
      ...prev,
      [messageId]: !prev[messageId],
    }));
  };

  const quickQuestions = [
    'What are the tax brackets for 2025?',
    'How is UIF calculated?',
    'What is the ETI for young workers?',
    'What is the tax threshold for under 65?',
    'How much is the primary rebate?',
  ];

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-700 to-blue-600 text-white p-4 shadow-md">
        <div className="flex items-center gap-3">
          <div className="bg-white rounded-full p-2">
            <svg
              className="w-6 h-6 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.07 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold">Payroll Tax Assistant</h2>
            <p className="text-blue-100 text-sm">
              SARS Tax Information • Data years: {taxYears.join(', ') || 'Loading...'}
            </p>
          </div>
        </div>
      </div>

      {/* Quick Questions */}
      <div className="bg-white border-b px-4 py-3">
        <div className="flex flex-wrap gap-2">
          {quickQuestions.map((question, idx) => (
            <button
              key={idx}
              onClick={() => setInputValue(question)}
              className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full transition-colors"
            >
              {question}
            </button>
          ))}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-2xl rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-800 shadow-md'
              }`}
            >
              {/* Message Content */}
              <div className="whitespace-pre-wrap">{message.content}</div>

              {/* Sources Toggle */}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <button
                    onClick={() => toggleSources(message.id)}
                    className={`text-sm flex items-center gap-1 ${
                      message.role === 'user'
                        ? 'text-blue-200 hover:text-blue-100'
                        : 'text-blue-600 hover:text-blue-700'
                    }`}
                  >
                    <svg
                      className={`w-4 h-4 transition-transform ${showSources[message.id] ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                    {showSources[message.id] ? 'Hide' : 'Show'} {message.sources.length} Sources
                  </button>

                  {showSources[message.id] && (
                    <div className="mt-2 space-y-2">
                      {message.sources.map((source, idx) => (
                        <div
                          key={source.id}
                          className={`text-xs rounded p-2 ${
                            message.role === 'user'
                              ? 'bg-blue-700 text-blue-100'
                              : 'bg-gray-50 text-gray-600'
                          }`}
                        >
                          <div className="flex justify-between items-start">
                            <span className="font-medium">
                              Source {idx + 1}: {source.metadata?.category || 'General'}{' '}
                              ({source.metadata?.tax_year || 'N/A'})
                            </span>
                            <span className="text-xs opacity-75">
                              {source.relevance}% match
                            </span>
                          </div>
                          <p className="mt-1 truncate">{source.content}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-lg px-4 py-3 shadow-md">
              <div className="flex items-center gap-2 text-gray-500">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-sm">Searching tax knowledge base...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t p-4">
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          {/* Category Filter */}
          <div className="flex items-center gap-4">
            <label className="text-sm text-gray-600">Filter by:</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          {/* Input Field */}
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about South African payroll tax..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isLoading ? (
                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              )}
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default PayrollAssistant;