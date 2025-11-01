'use server';

import { createStreamableValue } from 'ai/rsc';
import { CoreMessage, streamText } from 'ai';
import { openai, createOpenAI } from '@ai-sdk/openai';
import { env } from 'process';
import { Weather } from '@/components/weather';
import { generateText } from 'ai';
import { createStreamableUI } from 'ai/rsc';
import { ReactNode } from 'react';
import { z } from 'zod';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  display?: ReactNode;
}


// Streaming Chat 
export async function continueTextConversation(messages: CoreMessage[]) {
  // Use custom baseURL and model if provided
  const openaiUrl = process.env.OPENAI_URL;
  const openaiModel = process.env.OPENAI_MODEL || 'gpt-4-turbo';
  const openaiProvider = openaiUrl
    ? createOpenAI({ baseURL: openaiUrl, apiKey: process.env.OPENAI_API_KEY })
    : openai;

  const result = await streamText({
    model: openaiProvider(openaiModel),
    messages,
  });

  const stream = createStreamableValue(result.textStream);
  return stream.value;
}

// Gen UIs 
export async function continueConversation(history: Message[]) {
  const stream = createStreamableUI();

  const openaiUrl = process.env.OPENAI_URL;
  const openaiModel = process.env.OPENAI_MODEL || 'gpt-3.5-turbo';
  const openaiProvider = openaiUrl
    ? createOpenAI({ baseURL: openaiUrl, apiKey: process.env.OPENAI_API_KEY })
    : openai;

  const { text, toolResults } = await generateText({
    model: openaiProvider(openaiModel),
    system: 'You are a friendly weather assistant!',
    messages: history,
    tools: {
      showWeather: {
        description: 'Show the weather for a given location.',
        parameters: z.object({
          city: z.string().describe('The city to show the weather for.'),
          unit: z
            .enum(['F'])
            .describe('The unit to display the temperature in'),
        }),
        execute: async ({ city, unit }) => {
          stream.done(<Weather city={city} unit={unit} />);
          return `Here's the weather for ${city}!`;
        },
      },
    },
  });

  return {
    messages: [
      ...history,
      {
        role: 'assistant' as const,
        content:
          text || toolResults.map(toolResult => toolResult.result).join(),
        display: stream.value,
      },
    ],
  };
}

// Utils
export async function checkAIAvailability() {
  const envVarExists = !!process.env.OPENAI_API_KEY;
  return envVarExists;
}