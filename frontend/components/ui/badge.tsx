import * as React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  tone?: 'default' | 'muted' | 'accent' | 'domain';
}

export function Badge({ className, tone = 'default', ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium',
        tone === 'default' && 'border-indigo-400/30 bg-indigo-500/15 text-indigo-100',
        tone === 'muted' && 'border-white/10 bg-white/5 text-slate-200',
        tone === 'accent' && 'border-cyan-400/30 bg-cyan-500/10 text-cyan-100',
        tone === 'domain' && 'border-amber-400/30 bg-amber-500/10 text-amber-100',
        className
      )}
      {...props}
    />
  );
}
