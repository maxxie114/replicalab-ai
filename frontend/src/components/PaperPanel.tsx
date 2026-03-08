import { FileText, FlaskConical, Target, Microscope } from 'lucide-react';
import type { PaperSummary } from '@/types';
import { cn } from '@/lib/utils';

interface PaperPanelProps {
  paper: PaperSummary;
  seed: number;
  template: string;
  difficulty: string;
  round: number;
  maxRounds: number;
  className?: string;
}

export default function PaperPanel({
  paper,
  seed,
  template,
  difficulty,
  round,
  maxRounds,
  className,
}: PaperPanelProps) {
  return (
    <div className={cn('flex flex-col gap-4 overflow-y-auto', className)}>
      <div className="rounded-lg border border-border bg-card p-4">
        <div className="mb-3 flex items-center gap-2">
          <FileText className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-semibold">Original Paper</h2>
        </div>
        <h3 className="mb-2 text-base font-medium leading-snug">{paper.title}</h3>
        <div className="space-y-2 text-sm text-muted-foreground">
          <div className="flex items-start gap-2">
            <Target className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
            <div><span className="font-medium text-foreground">Hypothesis: </span>{paper.hypothesis}</div>
          </div>
          <div className="flex items-start gap-2">
            <Microscope className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
            <div><span className="font-medium text-foreground">Method: </span>{paper.method}</div>
          </div>
          <div className="flex items-start gap-2">
            <FlaskConical className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
            <div><span className="font-medium text-foreground">Key Finding: </span>{paper.key_finding}</div>
          </div>
        </div>
      </div>
      <div className="rounded-lg border border-border bg-card p-4">
        <h3 className="mb-3 text-sm font-semibold">Original Protocol</h3>
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
        <h3 className="mb-3 text-sm font-semibold">Episode Info</h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <Stat label="Seed" value={seed.toString()} />
          <Stat label="Template" value={template.replace(/_/g, ' ')} />
          <Stat label="Difficulty" value={difficulty} />
          <Stat label="Round" value={`${round} / ${maxRounds}`} highlight={round >= maxRounds} />
        </div>
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
