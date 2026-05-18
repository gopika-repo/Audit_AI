"use client";

import { useState } from 'react';
import { ChevronDown, ChevronUp, Bot } from 'lucide-react';
import type { ChatThreadMessage } from '@/hooks/useChat';
import { Avatar } from '@/components/ui/avatar';
import { Card, CardContent } from '@/components/ui/card';
import { SourceCard } from './SourceCard';
import { formatDate } from '@/lib/utils';

export function ChatMessage({ message }: { message: ChatThreadMessage }) {
  const [showSources, setShowSources] = useState<boolean>(true);
  const isAssistant = message.role === 'assistant';

  if (!isAssistant) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-3xl bg-indigo-500 px-4 py-3 text-white shadow-lg shadow-indigo-500/20">
          <div className="text-sm leading-6">{message.content}</div>
          <div className="mt-2 text-xs text-indigo-100/80">{formatDate(message.timestamp)}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3">
      <Avatar className="mt-1">
        <Bot className="h-5 w-5" />
      </Avatar>
      <div className="w-full space-y-3">
        <Card>
          <CardContent className="space-y-3 p-4">
            <div className="text-sm leading-6 text-slate-100">{message.content}</div>
            <div className="text-xs text-slate-400">{formatDate(message.timestamp)}</div>
            {message.sources && message.sources.length > 0 ? (
              <button
                type="button"
                className="inline-flex items-center gap-2 text-xs text-indigo-200 transition hover:text-indigo-100"
                onClick={() => setShowSources((current) => !current)}
              >
                Sources {showSources ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
              </button>
            ) : null}
          </CardContent>
        </Card>

        {showSources && message.sources && message.sources.length > 0 ? (
          <div className="grid gap-3 md:grid-cols-2">
            {message.sources.map((source) => (
              <SourceCard key={`${source.project_id}-${source.chunk_type}-${source.score}`} source={source} />
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}
