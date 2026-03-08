import { ClipboardList, ArrowRight } from 'lucide-react';
import type { Protocol, PaperSummary } from '@/types';
import { cn } from '@/lib/utils';

interface ProtocolPanelProps {
  protocol: Protocol | null;
  paper: PaperSummary;
  className?: string;
}

export default function ProtocolPanel({ protocol, paper, className }: ProtocolPanelProps) {
  if (!protocol) {
    return (
      <div className={cn('rounded-lg border border-border bg-card p-4', className)}>
        <div className="flex items-center gap-2">
          <ClipboardList className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-semibold">Current Protocol</h2>
        </div>
        <p className="mt-4 text-center text-sm text-muted-foreground">No protocol proposed yet</p>
      </div>
    );
  }

  return (
    <div className={cn('rounded-lg border border-border bg-card p-4', className)}>
      <div className="mb-3 flex items-center gap-2">
        <ClipboardList className="h-4 w-4 text-primary" />
        <h2 className="text-sm font-semibold">Current Protocol</h2>
      </div>
      <div className="space-y-2.5">
        <DiffRow label="Sample Size" original={paper.original_sample_size.toString()} current={protocol.sample_size.toString()} />
        <DiffRow label="Technique" original={paper.original_technique} current={protocol.technique} />
        <DiffRow label="Duration" original={`${paper.original_duration_days} days`} current={`${protocol.duration_days} days`} />
        <DiffRow label="Controls" original={paper.original_controls.join(', ')} current={protocol.controls.join(', ')} />
        <div className="pt-1">
          <div className="mb-1 text-xs font-medium text-muted-foreground">Equipment</div>
          <div className="flex flex-wrap gap-1">
            {protocol.required_equipment.map((e) => (<Tag key={e} label={e} />))}
          </div>
        </div>
        <div>
          <div className="mb-1 text-xs font-medium text-muted-foreground">Reagents</div>
          <div className="flex flex-wrap gap-1">
            {protocol.required_reagents.map((r) => (<Tag key={r} label={r} />))}
          </div>
        </div>
      </div>
    </div>
  );
}

function DiffRow({ label, original, current }: { label: string; original: string; current: string }) {
  const changed = original !== current;
  return (
    <div className="rounded-md bg-muted/50 px-2 py-1.5 text-xs">
      <div className="mb-0.5 font-medium text-muted-foreground">{label}</div>
      <div className="flex items-center gap-1.5">
        <span className={cn(changed && 'line-through text-muted-foreground/60')}>{original}</span>
        {changed && (<><ArrowRight className="h-3 w-3 text-primary" /><span className="font-medium text-primary">{current}</span></>)}
        {!changed && <span className="text-lab-manager text-[10px]">unchanged</span>}
      </div>
    </div>
  );
}

function Tag({ label }: { label: string }) {
  return <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">{label.replace(/_/g, ' ')}</span>;
}
