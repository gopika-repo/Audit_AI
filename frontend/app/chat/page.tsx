import { ChatInterface } from '@/components/chat/ChatInterface';

export default function ChatPage({
  searchParams
}: {
  searchParams: { question?: string };
}) {
  const initialQuestion = searchParams.question;

  return (
    <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-4xl font-semibold text-white">AI Chat</h1>
        <p className="mt-3 max-w-3xl text-slate-300">Ask questions about projects, architecture, and engineering workflows. Responses include cited sources from the knowledge base.</p>
      </div>
      <ChatInterface initialQuestion={initialQuestion} />
    </main>
  );
}
