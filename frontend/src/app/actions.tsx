'use server';

export interface CoreMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

const GROQ_API_URL = process.env.GROQ_API_URL;

if (!GROQ_API_URL) {
  throw new Error('GROQ_API_URL environment variable is not set');
}

/**
 * Query the database using natural language
 * @param messages - Array of conversation messages
 * @returns The assistant's response with data
 */
export async function continueTextConversation(messages: CoreMessage[]): Promise<string> {
  try {
    const userQuestion = messages[messages.length - 1].content;

    const response = await fetch(`${GROQ_API_URL}/api/data/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: userQuestion,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Data query API error response:', errorText);
      throw new Error(`Data query API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    // Return the formatted answer from the backend
    if (data.success) {
      return data.answer;
    } else {
      throw new Error(data.error || 'Unknown error occurred');
    }
  } catch (error) {
    console.error('Error calling data query API:', error);
    throw error;
  }
}

/**
 * Check if the backend API is available
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
    console.error('Error checking backend API availability:', error);
    return false;
  }
}