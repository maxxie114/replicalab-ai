import { CheckCircle, XCircle, AlertCircle, AlertTriangle } from 'lucide-react';
import type { JudgeAudit } from '@/types';
import { cn, verdictColor } from '@/lib/utils';
import CharacterAvatar from '@/components/CharacterAvatar';

interface JudgeAuditPanelProps {
  audit: JudgeAudit | null;
  className?: string;
}

export default function JudgeAuditPanel({ audit, className }: JudgeAuditPanelProps) {
  if (!audit) return null;

  const hasCaveats = audit.verdict === 'accept' && audit.top_failure_reasons.length > 0;
  const VerdictIcon =
    hasCaveats
      ? AlertTriangle
      : audit.verdict === 'success' || audit.verdict === 'accept'
      ? CheckCircle
      : audit.verdict === 'failure' || audit.verdict === 'reject'
        ? XCircle
        : AlertCircle;
  const verdictLabel = hasCaveats
    ? 'Accept with caveats'
    : audit.verdict.charAt(0).toUpperCase() + audit.verdict.slice(1);
  const reasonsLabel = hasCaveats ? 'Caveats to address' : 'Failure Reasons';
  const reasonsColor = hasCaveats ? 'text-judge' : 'text-destructive';

  return (
    <div className={cn('rounded-lg border border-judge/30 bg-judge/5 p-4', className)}>
      <div className="mb-3 flex items-center gap-3">
        <CharacterAvatar role="judge" size="sm" />
        <div>
          <h2 className="text-sm font-semibold">Judge Aldric's Verdict</h2>
          <div className={cn('flex items-center gap-1 text-xs font-semibold', hasCaveats ? 'text-judge' : verdictColor(audit.verdict))}>
            <VerdictIcon className="h-3.5 w-3.5" />
            {verdictLabel}
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
          <h3 className={cn('mb-1.5 text-xs font-medium', reasonsColor)}>{reasonsLabel}</h3>
          <ul className="space-y-1">
            {audit.top_failure_reasons.map((reason, i) => (
              <li key={i} className={cn('flex items-start gap-1.5 text-sm', reasonsColor)}>
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
