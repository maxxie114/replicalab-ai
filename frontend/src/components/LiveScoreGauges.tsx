import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';
import type { NegotiationMessage, Protocol, LabConstraints, PaperSummary } from '@/types';
import { cn, formatScore } from '@/lib/utils';

interface LiveScoreGaugesProps {
  conversation: NegotiationMessage[];
  protocol: Protocol | null;
  labConstraints: LabConstraints;
  paper: PaperSummary;
  className?: string;
}

function estimateScores(
  conversation: NegotiationMessage[],
  protocol: Protocol | null,
  lab: LabConstraints,
  paper: PaperSummary,
) {
  if (!protocol) return { rigor: 0.3, feasibility: 0.3, fidelity: 0.3 };

  // Estimate rigor: based on sample size relative to original, controls count
  const sampleRatio = paper.original_sample_size > 0
    ? Math.min(protocol.sample_size / paper.original_sample_size, 1)
    : 0.5;
  const controlRatio = paper.original_controls.length > 0
    ? Math.min(protocol.controls.length / paper.original_controls.length, 1)
    : 0.5;
  const rigor = Math.min(0.95, sampleRatio * 0.5 + controlRatio * 0.3 + 0.2);

  // Estimate feasibility: budget check, equipment availability
  const budgetOk = lab.budget_remaining > 0 ? 0.7 : 0.2;
  const equipAvail = protocol.required_equipment.length > 0
    ? protocol.required_equipment.filter((e) => lab.equipment_available.includes(e)).length /
      protocol.required_equipment.length
    : 0.8;
  const feasibility = Math.min(0.95, budgetOk * 0.5 + equipAvail * 0.3 + 0.2);

  // Estimate fidelity: technique match, duration match
  const techMatch = protocol.technique === paper.original_technique ? 0.4 : 0.15;
  const durRatio = paper.original_duration_days > 0
    ? 1 - Math.abs(protocol.duration_days - paper.original_duration_days) / paper.original_duration_days
    : 0.5;
  const fidelity = Math.min(0.95, techMatch + Math.max(0, durRatio) * 0.35 + 0.2);

  // Add negotiation bonus (more rounds = more refinement)
  const rounds = conversation.length;
  const bonus = Math.min(0.05, rounds * 0.01);

  return {
    rigor: Math.min(0.95, rigor + bonus),
    feasibility: Math.min(0.95, feasibility + bonus),
    fidelity: Math.min(0.95, fidelity + bonus),
  };
}

export default function LiveScoreGauges({
  conversation,
  protocol,
  labConstraints,
  paper,
  className,
}: LiveScoreGaugesProps) {
  const scores = useMemo(
    () => estimateScores(conversation, protocol, labConstraints, paper),
    [conversation, protocol, labConstraints, paper],
  );

  return (
    <div className={cn('rounded-lg border border-border bg-card p-3', className)}>
      <div className="mb-2 flex items-center gap-1.5">
        <Activity className="h-3.5 w-3.5 text-primary" />
        <span className="text-xs font-semibold">Live Estimate</span>
        <span className="ml-auto text-[10px] text-muted-foreground">updates each round</span>
      </div>
      <div className="space-y-2">
        <GaugeRow label="Rigor" value={scores.rigor} color="bg-scientist" />
        <GaugeRow label="Feasibility" value={scores.feasibility} color="bg-lab-manager" />
        <GaugeRow label="Fidelity" value={scores.fidelity} color="bg-judge" />
      </div>
    </div>
  );
}

function GaugeRow({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="mb-0.5 flex items-baseline justify-between text-[11px]">
        <span className="font-medium text-muted-foreground">{label}</span>
        <motion.span
          className="font-bold tabular-nums"
          key={Math.round(value * 100)}
          initial={{ scale: 1.3, color: 'var(--color-primary)' }}
          animate={{ scale: 1, color: 'var(--color-foreground)' }}
          transition={{ duration: 0.3 }}
        >
          {formatScore(value)}
        </motion.span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
        <motion.div
          className={cn('h-full rounded-full', color)}
          initial={{ width: 0 }}
          animate={{ width: `${value * 100}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}
