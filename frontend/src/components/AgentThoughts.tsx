import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, ChevronDown, ChevronUp, Eye, CheckCircle, XCircle } from 'lucide-react';
import type { NegotiationMessage, LabConstraints, Protocol } from '@/types';
import { cn } from '@/lib/utils';
import CharacterAvatar from '@/components/CharacterAvatar';

interface AgentThoughtsProps {
  messages: NegotiationMessage[];
  labConstraints: LabConstraints;
  protocol: Protocol | null;
  className?: string;
}

export default function AgentThoughts({
  messages,
  labConstraints,
  protocol,
  className,
}: AgentThoughtsProps) {
  const [expanded, setExpanded] = useState(true);

  if (messages.length === 0) return null;

  const lastScientist = [...messages].reverse().find((m) => m.role === 'scientist');
  const lastLabManager = [...messages].reverse().find((m) => m.role === 'lab_manager');

  return (
    <div className={cn('rounded-lg border border-border bg-card overflow-hidden', className)}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 px-4 py-2.5 text-left hover:bg-muted/50 transition-colors"
      >
        <Brain className="h-4 w-4 text-primary" />
        <span className="text-xs font-semibold">Agent Thinking</span>
        <Eye className="ml-1 h-3 w-3 text-muted-foreground" />
        <span className="ml-auto">
          {expanded ? <ChevronUp className="h-3.5 w-3.5 text-muted-foreground" /> : <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />}
        </span>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="grid grid-cols-2 gap-2 border-t border-border p-3">
              {/* Scientist's reasoning */}
              <div className="rounded-md border border-scientist/20 bg-scientist/5 p-2.5">
                <div className="mb-2 flex items-center gap-1.5">
                  <CharacterAvatar role="scientist" size="sm" />
                  <span className="text-[10px] font-bold text-scientist">Dr. Elara's Reasoning</span>
                </div>
                {lastScientist ? (
                  <div className="space-y-1.5 text-[11px]">
                    {lastScientist.action_type && (
                      <div className="flex items-center gap-1">
                        <span className="font-medium text-muted-foreground">Strategy:</span>
                        <span className="rounded-full bg-scientist/10 px-1.5 py-0.5 text-[10px] font-semibold text-scientist">
                          {lastScientist.action_type.replace(/_/g, ' ')}
                        </span>
                      </div>
                    )}
                    <p className="leading-relaxed text-muted-foreground">
                      {lastScientist.message.length > 150
                        ? lastScientist.message.slice(0, 150) + '...'
                        : lastScientist.message}
                    </p>
                    {protocol && (
                      <div className="mt-1 rounded border border-scientist/10 bg-scientist/5 p-1.5">
                        <span className="text-[9px] font-semibold text-scientist/70">PROPOSED</span>
                        <div className="mt-0.5 grid grid-cols-2 gap-x-2 text-[10px] text-muted-foreground">
                          <span>Samples: {protocol.sample_size}</span>
                          <span>Days: {protocol.duration_days}</span>
                          <span>Tech: {protocol.technique}</span>
                          <span>Controls: {protocol.controls.length}</span>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-[11px] text-muted-foreground italic">Waiting to propose...</p>
                )}
              </div>

              {/* Lab Manager's constraint analysis */}
              <div className="rounded-md border border-lab-manager/20 bg-lab-manager/5 p-2.5">
                <div className="mb-2 flex items-center gap-1.5">
                  <CharacterAvatar role="lab_manager" size="sm" />
                  <span className="text-[10px] font-bold text-lab-manager">Takuma's Analysis</span>
                </div>
                {lastLabManager ? (
                  <div className="space-y-1.5 text-[11px]">
                    {/* Constraint checks */}
                    <div className="space-y-0.5">
                      <ConstraintCheck
                        label="Budget"
                        ok={labConstraints.budget_remaining > 0}
                        detail={`$${labConstraints.budget_remaining.toLocaleString()} remaining`}
                      />
                      <ConstraintCheck
                        label="Equipment"
                        ok={labConstraints.equipment_available.length > 0}
                        detail={`${labConstraints.equipment_available.length} items available`}
                      />
                      <ConstraintCheck
                        label="Reagents"
                        ok={labConstraints.reagents_available.length > 0}
                        detail={`${labConstraints.reagents_available.length} in stock`}
                      />
                      <ConstraintCheck
                        label="Staff"
                        ok={labConstraints.staff_count > 0}
                        detail={`${labConstraints.staff_count} available`}
                      />
                      <ConstraintCheck
                        label="Conflicts"
                        ok={labConstraints.booking_conflicts.length === 0}
                        detail={labConstraints.booking_conflicts.length > 0 ? `${labConstraints.booking_conflicts.length} conflict(s)` : 'None'}
                      />
                    </div>
                    <p className="leading-relaxed text-muted-foreground">
                      {lastLabManager.message.length > 100
                        ? lastLabManager.message.slice(0, 100) + '...'
                        : lastLabManager.message}
                    </p>
                  </div>
                ) : (
                  <p className="text-[11px] text-muted-foreground italic">Waiting for proposal...</p>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function ConstraintCheck({ label, ok, detail }: { label: string; ok: boolean; detail: string }) {
  return (
    <div className="flex items-center gap-1 text-[10px]">
      {ok ? (
        <CheckCircle className="h-3 w-3 text-lab-manager" />
      ) : (
        <XCircle className="h-3 w-3 text-destructive" />
      )}
      <span className="font-medium">{label}</span>
      <span className="ml-auto text-muted-foreground">{detail}</span>
    </div>
  );
}
