import Link from 'next/link';

export default function NotFoundPage() {
  return (
    <main className="mx-auto flex min-h-[60vh] max-w-3xl items-center justify-center px-4 py-16 text-center">
      <div className="space-y-4 rounded-3xl border border-white/10 bg-white/5 p-8">
        <h1 className="text-3xl font-semibold text-white">Page not found</h1>
        <p className="text-sm text-slate-300">The page you&apos;re looking for does not exist.</p>
        <Link href="/" className="inline-flex rounded-xl bg-indigo-500 px-4 py-2 text-sm font-medium text-white">
          Back home
        </Link>
      </div>
    </main>
  );
}
