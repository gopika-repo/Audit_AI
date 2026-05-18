import Link from 'next/link';
import { Bot, LayoutDashboard, Network, Orbit, Search, Settings2 } from 'lucide-react';

const sidebarItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/projects', label: 'Projects', icon: Orbit },
  { href: '/chat', label: 'AI Chat', icon: Bot },
  { href: '/dashboard#search', label: 'Knowledge Search', icon: Search },
  { href: '/dashboard#domains', label: 'Domains', icon: Network },
  { href: '/dashboard#settings', label: 'Settings', icon: Settings2 }
];

export function Sidebar() {
  return (
    <aside className="hidden h-full w-72 shrink-0 border-r border-white/10 bg-slate-950/60 px-5 py-6 xl:block">
      <div className="mb-6 text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Navigation</div>
      <div className="space-y-2">
        {sidebarItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center gap-3 rounded-2xl border border-white/5 bg-white/5 px-4 py-3 text-sm text-slate-200 transition hover:border-indigo-400/30 hover:bg-white/10 hover:text-white"
          >
            <item.icon className="h-4 w-4 text-indigo-300" />
            {item.label}
          </Link>
        ))}
      </div>
    </aside>
  );
}
