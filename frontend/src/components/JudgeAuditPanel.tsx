import { CheckCircle, XCircle, AlertCircle, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
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
          <div className="text-sm space-y-2">
            {audit.judge_notes.map((note, i) => (
              <ReactMarkdown
                key={i}
                components={{
                  h1: ({ children }) => <h1 className="text-base font-bold mt-3 mb-1">{children}</h1>,
                  h2: ({ children }) => <h2 className="text-sm font-semibold mt-2 mb-1 text-foreground">{children}</h2>,
                  h3: ({ children }) => <h3 className="text-xs font-semibold mt-2 mb-0.5 text-muted-foreground uppercase tracking-wide">{children}</h3>,
                  p: ({ children }) => <p className="leading-relaxed">{children}</p>,
                  ul: ({ children }) => <ul className="list-disc list-inside space-y-0.5 ml-2">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-inside space-y-0.5 ml-2">{children}</ol>,
                  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                  strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
                  hr: () => <hr className="border-border my-2" />,
                  blockquote: ({ children }) => <blockquote className="border-l-2 border-judge/50 pl-3 italic text-muted-foreground">{children}</blockquote>,
                }}
              >
                {note}
              </ReactMarkdown>
            ))}
          </div>
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
