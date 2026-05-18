"use client";

import { useCallback, useEffect, useMemo, useState } from 'react';
import { chatApi } from '@/lib/api';
import type { ChatMessage, ChatSource } from '@/lib/types';

const STORAGE_KEY = 'ai-onboarding-conversation-id';

export interface ChatThreadMessage extends ChatMessage {
  id: string;
  sources?: ChatSource[];
}

export function useChat() {
  const [conversationId, setConversationId] = useState<string>('');
  const [messages, setMessages] = useState<ChatThreadMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const storedConversationId = window.localStorage.getItem(STORAGE_KEY);
    const activeConversationId = storedConversationId ?? crypto.randomUUID();
    window.localStorage.setItem(STORAGE_KEY, activeConversationId);
    setConversationId(activeConversationId);

    void chatApi
      .getHistory(activeConversationId)
      .then((history) => {
        setMessages(
          history.messages.map((message, index) => ({
            ...message,
            id: `${activeConversationId}-${index}`
          }))
        );
      })
      .catch(() => {
        setMessages([]);
      });
  }, []);

  const canSend = useMemo(() => !isLoading && conversationId.length > 0, [conversationId, isLoading]);

  const sendMessage = useCallback(
    async (message: string, userId?: string): Promise<void> => {
      if (!message.trim() || !conversationId) {
        return;
      }

      const outgoing: ChatThreadMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
        sources: []
      };

      setMessages((current) => [...current, outgoing]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await chatApi.sendMessage({
          message,
          conversation_id: conversationId,
          user_id: userId
        });

        window.localStorage.setItem(STORAGE_KEY, response.conversation_id);
        setConversationId(response.conversation_id);

        const assistantMessage: ChatThreadMessage = {
          id: response.message_id,
          role: 'assistant',
          content: response.response,
          timestamp: response.timestamp,
          sources: response.sources
        };

        setMessages((current) => [...current, assistantMessage]);
      } catch (requestError) {
        const fallbackMessage = requestError instanceof Error ? requestError.message : 'Message failed';
        setError(fallbackMessage);
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId]
  );

  const clearConversation = useCallback(async (): Promise<void> => {
    if (!conversationId) {
      return;
    }

    await chatApi.clearHistory(conversationId);
    setMessages([]);
  }, [conversationId]);

  return {
    conversationId,
    messages,
    isLoading,
    error,
    canSend,
    sendMessage,
    clearConversation
  };
}
