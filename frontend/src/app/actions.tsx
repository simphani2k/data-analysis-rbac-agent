'use server';

export interface CoreMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

const GROQ_API_URL = process.env.GROQ_API_URL || 'http://54.183.212.95:8000';
const GROQ_MODEL = process.env.GROQ_MODEL || 'llama-3.3-70b-versatile';

/**
 * Continue a conversation with the Groq API
 * @param messages - Array of conversation messages
 * @returns The assistant's response
 */
export async function continueTextConversation(messages: CoreMessage[]): Promise<string> {
  try {
    const response = await fetch(`${GROQ_API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: messages[messages.length - 1].content,
        model: GROQ_MODEL,
        temperature: 0.7,
        max_tokens: 1024,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Groq API error response:', errorText);
      throw new Error(`Groq API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error('Error calling Groq API:', error);
    throw error;
  }
}

/**
 * Check if the Groq API is available
 * @returns True if the API is available, false otherwise
 */
export async function checkAIAvailability(): Promise<boolean> {
  try {
    const response = await fetch(`${GROQ_API_URL}/health`, {
      method: 'GET',
      cache: 'no-store',
    });
    return response.ok;
  } catch (error) {
    console.error('Error checking Groq API availability:', error);
    return false;
  }
}