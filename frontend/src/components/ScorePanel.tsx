import { Trophy, AlertTriangle } from 'lucide-react';
import type { ScoreBreakdown } from '@/types';
import { cn, formatScore, formatReward } from '@/lib/utils';

interface ScorePanelProps {
  scores: ScoreBreakdown | null;
  done: boolean;
  className?: string;
}

export default function ScorePanel({ scores, done, className }: ScorePanelProps) {
  return (
    <div className={cn('rounded-lg border border-border bg-card p-4', className)}>
      <div className="mb-3 flex items-center gap-2">
        <Trophy className="h-4 w-4 text-judge" />
        <h2 className="text-sm font-semibold">Scores</h2>
        {done && (
          <span className="ml-auto rounded-full bg-judge/10 px-2 py-0.5 text-xs font-medium text-judge">Final</span>
        )}
      </div>
      {!scores ? (
        <p className="text-center text-sm text-muted-foreground">{done ? 'No scores available' : 'Scores appear after episode ends'}</p>
      ) : (
        <div className="space-y-3">
          <ScoreBar label="Rigor" value={scores.rigor} color="bg-scientist" />
          <ScoreBar label="Feasibility" value={scores.feasibility} color="bg-lab-manager" />
          <ScoreBar label="Fidelity" value={scores.fidelity} color="bg-judge" />
          <div className="border-t border-border pt-3">
            <div className="flex items-baseline justify-between">
              <span className="text-sm font-medium">Total Reward</span>
              <span className="text-xl font-bold text-primary">{formatReward(scores.total_reward)}</span>
            </div>
            <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
              <span className="text-lab-manager">+{formatReward(scores.efficiency_bonus)} eff</span>
              <span className="text-scientist">+{formatReward(scores.communication_bonus)} comm</span>
              {scores.penalties > 0 && <span className="text-destructive">-{formatReward(scores.penalties)} pen</span>}
            </div>
          </div>
          {scores.penalty_reasons.length > 0 && (
            <div className="rounded-md bg-destructive/5 border border-destructive/20 p-2">
              <div className="mb-1 flex items-center gap-1 text-xs font-medium text-destructive">
                <AlertTriangle className="h-3 w-3" />Penalties
              </div>
              <ul className="space-y-0.5 text-xs text-muted-foreground">
                {scores.penalty_reasons.map((r, i) => <li key={i}>• {r}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ScoreBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="mb-1 flex items-baseline justify-between text-xs">
        <span className="font-medium">{label}</span>
        <span className="text-muted-foreground">{formatScore(value)}</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div className={cn('h-full rounded-full transition-all duration-500', color)} style={{ width: `${value * 100}%` }} />
      </div>
    </div>
  );
}
