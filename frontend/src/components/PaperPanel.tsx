import { FileText, FlaskConical, Target, Microscope, Copy, Check, ArrowRight } from 'lucide-react';
import { useState } from 'react';
import type { PaperSummary } from '@/types';
import { cn } from '@/lib/utils';

interface PaperPanelProps {
  paper: PaperSummary;
  seed: number;
  template: string;
  difficulty: string;
  round: number;
  maxRounds: number;
  episodeId?: string;
  className?: string;
}

export default function PaperPanel({
  paper,
  seed,
  template,
  difficulty,
  round,
  maxRounds,
  episodeId,
  className,
}: PaperPanelProps) {
  const [copied, setCopied] = useState(false);
  const templateLabel = template.replace(/_/g, ' ');

  function copyEpisodeId() {
    if (!episodeId) return;
    navigator.clipboard.writeText(episodeId);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }
  return (
    <div className={cn('flex flex-col gap-4 overflow-y-auto', className)}>
      <div className="rounded-lg border border-border bg-card p-4">
        <div className="mb-3 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-primary" />
            <h2 className="text-sm font-semibold">Source Paper</h2>
          </div>
          <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">
            PDF to task
          </span>
        </div>
        <div className="rounded-lg border border-border/60 bg-muted/30 p-3">
          <div className="mb-2 flex items-center gap-2 text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
            <span className="rounded bg-destructive/10 px-1.5 py-0.5 font-semibold text-destructive">PDF</span>
            <span>Seeded replication brief</span>
          </div>
          <h3 className="mb-2 text-base font-medium leading-snug">{paper.title}</h3>
          <p className="text-sm text-muted-foreground">
            ReplicaLab freezes this paper into a reproducible benchmark so the agents must preserve the
            claim while adapting to budget, compute, reagent, and scheduling constraints.
          </p>
        </div>
      </div>
      <div className="rounded-lg border border-border bg-card p-4">
        <div className="mb-3 flex items-center gap-2">
          <ArrowRight className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-semibold">Parsed Replication Brief</h3>
        </div>
        <div className="space-y-3 text-sm text-muted-foreground">
          <div className="flex items-start gap-2">
            <Target className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
            <div><span className="font-medium text-foreground">Objective: </span>{paper.hypothesis}</div>
          </div>
          <div className="flex items-start gap-2">
            <Microscope className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
            <div><span className="font-medium text-foreground">Original Method: </span>{paper.method}</div>
          </div>
          <div className="flex items-start gap-2">
            <FlaskConical className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
            <div><span className="font-medium text-foreground">Result To Preserve: </span>{paper.key_finding}</div>
          </div>
        </div>
      </div>
      <div className="rounded-lg border border-border bg-card p-4">
        <h3 className="mb-3 text-sm font-semibold">Original Experiment</h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <Stat label="Sample Size" value={paper.original_sample_size.toString()} />
          <Stat label="Technique" value={paper.original_technique} />
          <Stat label="Duration" value={`${paper.original_duration_days}d`} />
          <Stat label="Controls" value={paper.original_controls.length.toString()} />
        </div>
        <div className="mt-2 flex flex-wrap gap-1">
          {paper.original_controls.map((c) => (
            <span key={c} className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">{c.replace(/_/g, ' ')}</span>
          ))}
        </div>
      </div>
      <div className="rounded-lg border border-border bg-card p-4">
        <h3 className="mb-3 text-sm font-semibold">Benchmark Context</h3>
        {episodeId && (
          <button
            onClick={copyEpisodeId}
            className="mb-2 flex w-full items-center gap-1.5 rounded-md bg-muted/50 px-2 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted"
          >
            {copied ? <Check className="h-3 w-3 text-lab-manager" /> : <Copy className="h-3 w-3" />}
            <span className="font-mono truncate">{episodeId}</span>
          </button>
        )}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <Stat label="Seed" value={seed.toString()} />
          <Stat label="Family" value={templateLabel} />
          <Stat label="Difficulty" value={difficulty} />
          <Stat label="Round" value={`${round} / ${maxRounds}`} highlight={round >= maxRounds} />
        </div>
        <p className="mt-3 text-xs text-muted-foreground">
          Training and evaluation reuse this exact seed and scenario family so baseline and trained policies can
          be compared on the same task.
        </p>
      </div>
    </div>
  );
}

function Stat({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="rounded-md bg-muted/50 px-2 py-1.5">
      <div className="text-muted-foreground">{label}</div>
      <div className={cn('font-medium', highlight ? 'text-destructive' : 'text-foreground')}>{value}</div>
    </div>
  );
}
