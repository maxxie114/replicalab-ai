import { motion } from 'framer-motion';
import { GitCommitHorizontal, ArrowRight } from 'lucide-react';
import type { NegotiationMessage } from '@/types';
import { cn } from '@/lib/utils';

interface ProtocolTimelineProps {
  messages: NegotiationMessage[];
  className?: string;
}

interface ProtocolSnapshot {
  round: number;
  action_type: string;
  role: string;
  message: string;
}

export default function ProtocolTimeline({ messages, className }: ProtocolTimelineProps) {
  // Extract protocol-changing events
  const snapshots: ProtocolSnapshot[] = messages
    .filter((m) => m.action_type && ['propose_protocol', 'revise_protocol', 'suggest_alternative', 'accept', 'reject'].includes(m.action_type))
    .map((m) => ({
      round: m.round,
      action_type: m.action_type!,
      role: m.role,
      message: m.message.length > 100 ? m.message.slice(0, 100) + '...' : m.message,
    }));

  if (snapshots.length === 0) return null;

  return (
    <div className={cn('rounded-lg border border-border bg-card p-3', className)}>
      <div className="mb-3 flex items-center gap-1.5">
        <GitCommitHorizontal className="h-3.5 w-3.5 text-primary" />
        <span className="text-xs font-semibold">Protocol Evolution</span>
      </div>

      {/* Horizontal scrollable timeline */}
      <div className="overflow-x-auto">
        <div className="flex items-start gap-0 min-w-max">
          {snapshots.map((snap, i) => (
            <div key={i} className="flex items-start">
              <motion.div
                className="flex flex-col items-center"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                {/* Node */}
                <div
                  className={cn(
                    'flex h-7 w-7 items-center justify-center rounded-full border-2 text-[10px] font-bold',
                    snap.role === 'scientist'
                      ? 'border-scientist bg-scientist/10 text-scientist'
                      : 'border-lab-manager bg-lab-manager/10 text-lab-manager',
                  )}
                >
                  R{snap.round}
                </div>
                {/* Action label */}
                <span
                  className={cn(
                    'mt-1 rounded-full px-1.5 py-0.5 text-[9px] font-semibold',
                    snap.role === 'scientist'
                      ? 'bg-scientist/10 text-scientist'
                      : 'bg-lab-manager/10 text-lab-manager',
                  )}
                >
                  {snap.action_type.replace(/_/g, ' ')}
                </span>
                {/* Summary */}
                <div className="mt-1 w-28 text-center text-[10px] leading-tight text-muted-foreground">
                  {snap.message.slice(0, 60)}...
                </div>
              </motion.div>
              {/* Arrow connector */}
              {i < snapshots.length - 1 && (
                <div className="mt-2.5 flex items-center px-1">
                  <div className="h-px w-4 bg-border" />
                  <ArrowRight className="h-3 w-3 text-muted-foreground/40" />
                  <div className="h-px w-4 bg-border" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
