'use client';

import { Card } from "@/components/ui/card"
import { useState, useRef, useEffect } from 'react';
import { continueTextConversation, type CoreMessage } from '@/app/actions';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { IconArrowUp } from '@/components/ui/icons';
import AboutCard from "@/components/cards/aboutcard";
export const maxDuration = 30;

// Typing indicator component
function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 p-3">
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
  );
}

export default function Chat() {
  const [messages, setMessages] = useState<CoreMessage[]>([]);
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage, isLoading]);

  // Focus input on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  // Simulate streaming effect by displaying response character by character
  const streamResponse = async (response: string) => {
    setStreamingMessage('');
    const words = response.split(' ');

    for (let i = 0; i < words.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 50));
      setStreamingMessage(prev => prev + (i > 0 ? ' ' : '') + words[i]);
    }

    return response;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    const newMessages: CoreMessage[] = [
      ...messages,
      { content: userMessage, role: 'user' },
    ];

    setMessages(newMessages);
    setInput('');
    setIsLoading(true);
    setStreamingMessage('');

    try {
      const response = await continueTextConversation(newMessages);

      // Stream the response
      await streamResponse(response);

      setMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: response,
        },
      ]);
      setStreamingMessage('');
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = 'Sorry, I encountered an error. Please try again.';
      setMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: errorMessage,
        },
      ]);
      setStreamingMessage('');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="group w-full overflow-auto pb-32">
      {messages.length <= 0 ? (
        <AboutCard />
      ) : (
        <div className="max-w-3xl mx-auto mt-10 px-4">
          {messages.map((message, index) => (
            <div key={index} className="mb-6 flex">
              <div className={`${
                message.role === 'user'
                  ? 'bg-blue-500 text-white ml-auto'
                  : 'bg-gray-100 text-gray-900'
                } px-4 py-3 rounded-2xl max-w-[80%] shadow-sm`}>
                <div className="whitespace-pre-wrap break-words">
                  {message.content as string}
                </div>
              </div>
            </div>
          ))}

          {/* Show streaming message */}
          {streamingMessage && (
            <div className="mb-6 flex">
              <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-2xl max-w-[80%] shadow-sm">
                <div className="whitespace-pre-wrap break-words">
                  {streamingMessage}
                  <span className="inline-block w-1 h-4 bg-gray-900 ml-1 animate-pulse" />
                </div>
              </div>
            </div>
          )}

          {/* Show typing indicator */}
          {isLoading && !streamingMessage && (
            <div className="mb-6 flex">
              <TypingIndicator />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      )}

      <div className="fixed inset-x-0 bottom-0 bg-gradient-to-t from-white via-white to-transparent pb-6 pt-6">
        <div className="w-full max-w-3xl mx-auto px-4">
          <Card className="shadow-lg border-gray-200">
            <form onSubmit={handleSubmit} className="p-3">
              <div className="flex items-center gap-2">
                <Input
                  ref={textareaRef}
                  type="text"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="flex-1 border-0 focus-visible:ring-0 focus-visible:ring-offset-0 text-base"
                  placeholder="Ask me anything..."
                  disabled={isLoading}
                />
                <Button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="rounded-full h-10 w-10 p-0"
                >
                  <IconArrowUp />
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
}
