'use server';

import { createStreamableValue } from 'ai/rsc';
import { CoreMessage } from 'ai';
import { Weather } from '@/components/weather';
import { createStreamableUI } from 'ai/rsc';
import { ReactNode } from 'react';
import { z } from 'zod';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  display?: ReactNode;
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
    const stream = createStreamableValue(data.response);
    return stream.value;
  } catch (error) {
    console.error('Error calling Groq API:', error);
    throw error;
  }
}

// Gen UIs using Groq API
export async function continueConversation(history: Message[]) {
  const stream = createStreamableUI();
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
    
    if (isWeatherQuery) {
      // Extract city from message (simple approach)
      const cityMatch = messageText.match(/in\s+([a-z\s]+)/i);
      const city = cityMatch ? cityMatch[1].trim() : 'New York';
      stream.done(<Weather city={city} unit="F" />);
    }

    return {
      messages: [
        ...history,
        {
          role: 'assistant' as const,
          content: data.response,
          display: stream.value,
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
          display: stream.value,
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