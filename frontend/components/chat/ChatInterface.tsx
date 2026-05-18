"use client";

import { useEffect, useMemo, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { ChatInput } from './ChatInput';
import { ChatMessage } from './ChatMessage';
import { useChat } from '@/hooks/useChat';

const suggestedQuestions = [
  'Which projects use LangGraph?',
  'Explain the Research Agent',
  'What is our tech stack for NLP?',
  'How does the RAG pipeline work?'
];

export function ChatInterface({ initialQuestion }: { initialQuestion?: string }) {
  const { messages, sendMessage, isLoading, error } = useChat();
  const hasSentInitialQuestion = useRef<boolean>(false);

  useEffect(() => {
    if (!initialQuestion || hasSentInitialQuestion.current) {
      return;
    }

    hasSentInitialQuestion.current = true;
    void sendMessage(initialQuestion);
  }, [initialQuestion, sendMessage]);

  const renderedMessages = useMemo(
    () => messages.map((message) => <ChatMessage key={message.id} message={message} />),
    [messages]
  );

  return (
    <div className="grid gap-6 xl:grid-cols-[280px_minmax(0,1fr)]">
      <Card className="h-fit">
        <CardHeader>
          <CardTitle>Suggested Questions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {suggestedQuestions.map((question) => (
            <Button key={question} type="button" variant="secondary" className="w-full justify-start" onClick={() => void sendMessage(question)}>
              {question}
            </Button>
          ))}
        </CardContent>
      </Card>

      <div className="space-y-4">
        <ScrollArea className="max-h-[68vh] rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
          <div className="space-y-5">{renderedMessages}</div>
        </ScrollArea>

        {error ? <div className="rounded-2xl border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-100">{error}</div> : null}

        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
