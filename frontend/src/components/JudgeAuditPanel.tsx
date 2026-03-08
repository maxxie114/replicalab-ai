import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import type { JudgeAudit } from '@/types';
import { cn, verdictColor } from '@/lib/utils';
import CharacterAvatar from '@/components/CharacterAvatar';

interface JudgeAuditPanelProps {
  audit: JudgeAudit | null;
  className?: string;
}

export default function JudgeAuditPanel({ audit, className }: JudgeAuditPanelProps) {
  if (!audit) return null;

  const VerdictIcon =
    audit.verdict === 'success'
      ? CheckCircle
      : audit.verdict === 'failure'
        ? XCircle
        : AlertCircle;

  return (
    <div className={cn('rounded-lg border border-judge/30 bg-judge/5 p-4', className)}>
      <div className="mb-3 flex items-center gap-3">
        <CharacterAvatar role="judge" size="sm" />
        <div>
          <h2 className="text-sm font-semibold">Judge Aldric's Verdict</h2>
          <div className={cn('flex items-center gap-1 text-xs font-semibold', verdictColor(audit.verdict))}>
            <VerdictIcon className="h-3.5 w-3.5" />
            {audit.verdict.charAt(0).toUpperCase() + audit.verdict.slice(1)}
          </div>
        </div>
      </div>

      {audit.judge_notes.length > 0 && (
        <div className="mb-3">
          <h3 className="mb-1.5 text-xs font-medium text-muted-foreground">Notes</h3>
          <ul className="space-y-1">
            {audit.judge_notes.map((note, i) => (
              <li key={i} className="flex items-start gap-1.5 text-sm">
                <CheckCircle className="mt-0.5 h-3 w-3 shrink-0 text-lab-manager" />
                {note}
              </li>
            ))}
          </ul>
        </div>
      )}

      {audit.top_failure_reasons.length > 0 && (
        <div>
          <h3 className="mb-1.5 text-xs font-medium text-destructive">Failure Reasons</h3>
          <ul className="space-y-1">
            {audit.top_failure_reasons.map((reason, i) => (
              <li key={i} className="flex items-start gap-1.5 text-sm text-destructive">
                <XCircle className="mt-0.5 h-3 w-3 shrink-0" />
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
