import * as React from 'react';
import { cn } from '@/lib/utils';

export function Avatar({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('flex h-10 w-10 items-center justify-center rounded-full bg-indigo-500/20 text-indigo-100 ring-1 ring-indigo-400/30', className)} {...props} />;
}
