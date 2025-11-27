'use server';

import { Weather } from '@/components/weather';
import { ReactNode } from 'react';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  display?: ReactNode;
}

export interface CoreMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

// Simple streamable value replacement
function createSimpleStreamableValue(value: string) {
  return {
    value: (async function* () {
      yield value;
    })(),
  };
}

// Streaming Chat using Groq API
export async function continueTextConversation(messages: CoreMessage[]) {
  const groqApiUrl = process.env.GROQ_API_URL || 'http://3.80.111.127:8000';
  const groqModel = process.env.GROQ_MODEL || 'llama-3.3-70b-versatile';
  
  try {
    // Call Groq API
    const response = await fetch(`${groqApiUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: messages[messages.length - 1].content,
        model: groqModel,
        temperature: 0.7,
        max_tokens: 1024,
      }),
    });

    if (!response.ok) {
      throw new Error(`Groq API error: ${response.statusText}`);
    }

    const data = await response.json();
    return createSimpleStreamableValue(data.response);
  } catch (error) {
    console.error('Error calling Groq API:', error);
    throw error;
  }
}

// Gen UIs using Groq API
export async function continueConversation(history: Message[]) {
  const groqApiUrl = process.env.GROQ_API_URL || 'http://3.80.111.127:8000';
  const groqModel = process.env.GROQ_MODEL || 'llama-3.3-70b-versatile';

  try {
    const lastMessage = history[history.length - 1];
    
    // Call Groq API
    const response = await fetch(`${groqApiUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: lastMessage.content,
        model: groqModel,
        temperature: 0.7,
        max_tokens: 1024,
      }),
    });

    if (!response.ok) {
      throw new Error(`Groq API error: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Simple weather detection (you can enhance this with better NLP)
    const weatherKeywords = ['weather', 'temperature', 'forecast', 'climate'];
    const messageText = lastMessage.content.toLowerCase();
    const isWeatherQuery = weatherKeywords.some(keyword => messageText.includes(keyword));
    
    let displayComponent = null;
    if (isWeatherQuery) {
      // Extract city from message (simple approach)
      const cityMatch = messageText.match(/in\s+([a-z\s]+)/i);
      const city = cityMatch ? cityMatch[1].trim() : 'New York';
      displayComponent = <Weather city={city} unit="fahrenheit" />;
    }

    return {
      messages: [
        ...history,
        {
          role: 'assistant' as const,
          content: data.response,
          display: displayComponent,
        },
      ],
    };
  } catch (error) {
    console.error('Error calling Groq API:', error);
    return {
      messages: [
        ...history,
        {
          role: 'assistant' as const,
          content: 'Sorry, I encountered an error. Please try again.',
          display: null,
        },
      ],
    };
  }
}

// Utils
export async function checkAIAvailability() {
  const groqApiUrl = process.env.GROQ_API_URL || 'http://3.80.111.127:8000';
  
  try {
    const response = await fetch(`${groqApiUrl}/health`, {
      method: 'GET',
    });
    return response.ok;
  } catch (error) {
    console.error('Error checking Groq API availability:', error);
    return false;
  }
}