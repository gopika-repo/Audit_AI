"use client";

import { useState } from 'react';
import { SendHorizontal } from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';

export function ChatInput({
  onSend,
  isLoading
}: {
  onSend: (message: string) => Promise<void>;
  isLoading: boolean;
}) {
  const [value, setValue] = useState<string>('');

  return (
    <form
      className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl"
      onSubmit={async (event) => {
        event.preventDefault();
        const message = value.trim();
        if (!message) {
          return;
        }
        setValue('');
        await onSend(message);
      }}
    >
      <div className="space-y-3">
        <Textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Ask about a project, architecture decision, tech stack, or workflow..."
          aria-label="Chat message input"
        />
        <div className="flex justify-end">
          <Button type="submit" disabled={isLoading || value.trim().length === 0}>
            <SendHorizontal className="mr-2 h-4 w-4" />
            {isLoading ? 'Sending...' : 'Send'}
          </Button>
        </div>
      </div>
    </form>
  );
}
