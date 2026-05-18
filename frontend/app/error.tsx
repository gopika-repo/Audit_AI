"use client";

export default function ErrorPage({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <main className="mx-auto flex min-h-[60vh] max-w-3xl items-center justify-center px-4 py-16 text-center">
      <div className="space-y-4 rounded-3xl border border-red-400/20 bg-red-500/10 p-8 text-red-50">
        <h1 className="text-2xl font-semibold">Something went wrong</h1>
        <p className="text-sm text-red-100">{error.message}</p>
        <button type="button" onClick={reset} className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium text-white">
          Try again
        </button>
      </div>
    </main>
  );
}
